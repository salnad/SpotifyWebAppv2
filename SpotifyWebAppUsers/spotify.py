from flask import Blueprint, redirect, request, url_for, render_template, flash
from flask_login import login_required, current_user
import spotipy, json
from . import db
from .models import Room
from spotipy import oauth2

SPOTIPY_CLIENT_ID = '62067c3296db41bda75539a1749da1cb'
SPOTIPY_CLIENT_SECRET = '287d8a2554d14871bfda2f2b2577026c'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:5000/spotifyauth' # prolly needs to change
SCOPE = 'user-read-private user-read-playback-state user-modify-playback-state streaming'

spotify = Blueprint('spotify', __name__)

spotify_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE)

def song_in_queue(song,queue):
    for s in queue:
        if s['id'] == song['id']:
            s['votes']+= 1
            return True
    return False

def add_dict_to_queue(dict, queueStr):
    queue = json.loads(queueStr)
    if not song_in_queue(dict, queue):
        queue.append(dict)
    return json.dumps(queue)


def song_to_dict(song):
    result = {}
    result['id'] = song['id']
    result['votes'] = 0
    result['track_uri'] = song['uri']
    result['artists'] = [ a['name'] for a in song['artists']]
    result['track_title'] = song['name']
    return result

def play_song_from_id(song_uri, sp, device_id):
    sp.start_playback(device_id=device_id,uris=[song_uri])

@spotify.route('/spotifyauth')
@login_required
def auth_spotify():
    access_token = ""
    url = request.url
    code = spotify_oauth.parse_response_code(url)
    if code:
        token_info = spotify_oauth.get_access_token(code)
        access_token = token_info['access_token']
    if access_token:
        current_user.auth_token = access_token
        db.session.commit()
        flash('Reauthorized Spotify For Your Account')
        return redirect(url_for('main.profile'))
    else:
        auth_url = auth_url = spotify_oauth.get_authorize_url()
        return redirect(auth_url)

@spotify.route('/add', methods=['POST'])
@login_required
def add():
    query = request.form.get('query')
    room_id = request.form.get('room_id')
    try:
        spotify_object = spotipy.Spotify(current_user.auth_token)
        query_result = spotify_object.search(query)['tracks']['items']
        if len(query_result) > 0:
            query_result = query_result[0]
            query_dict = song_to_dict(query_result)
            current_room = Room.query.get(room_id)
            current_room.queue = add_dict_to_queue(query_dict, current_room.queue)
            db.session.commit()
            print(current_room.queue)
        return redirect(url_for('main.room',room_id=room_id))
    except:
        return redirect(url_for('spotify.auth_spotify'))

@spotify.route('/room-dashboard/<int:room_id>')
@login_required
def room_dashboard(room_id):
    current_room = Room.query.get(room_id)
    if current_user.id != current_room.owner_id:
        return redirect(url_for('main.room',room_id=room_id))
    try:
        spotify_object = spotipy.Spotify(current_user.auth_token)
        queue = json.loads(current_room.queue)
        devices = spotify_object.devices()['devices']
        device_name = "No Devices Active"
        if len(devices) > 0:
            device_name = devices[0]['name']
            if not spotify_object.current_playback() or not spotify_object.current_playback()['is_playing'] and len(queue) > 0:
                song_uri = queue.pop(0)['track_uri']
                play_song_from_id(song_uri, spotify_object, devices[0]['id'])
                current_room.queue = json.dumps(queue)
                db.session.commit()
        return render_template('roomdashboard.html', device_name=device_name, queue=queue, room_id=room_id)
    except:
        return redirect(url_for('spotify.auth_spotify'))
