from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Room
import json

def get_queue_as_list(queue):
    queue = json.loads(queue)
    queue = sorted(queue, key=lambda k: k['votes'], reverse=True)
    return queue


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    rooms = [room.room_id for room in Room.query.filter_by(owner_id=current_user.id).all()]
    auth_token = current_user.auth_token
    print(auth_token)
    return render_template('profile.html',name=current_user.username,rooms=rooms)

@main.route('/profile', methods=['POST'])
@login_required
def profile_post():
    if 'create_room' in request.form:
        room_dashboard_option = int(request.form.get('room_dashboard_option'))
        if room_dashboard_option == 0:
            new_room = Room(owner_id=current_user.id)
            db.session.add(new_room)
            db.session.commit()
            return redirect(url_for('spotify.room_dashboard',room_id=new_room.room_id))
        else:
            return redirect(url_for('spotify.room_dashboard',room_id=room_dashboard_option))
    elif 'join_room' in request.form:
        room_id = request.form['room_id']
        room = Room.query.get(room_id)
        if room:
            return redirect(url_for('main.room',room_id=room_id))
        else:
            flash('No room exists with that code')
            return redirect(url_for('main.profile'),code=303)

@main.route('/room/<int:room_id>')
@login_required
def room(room_id):
    current_room = Room.query.get(room_id)
    queue = get_queue_as_list(current_room.queue)
    return render_template('room.html', queue=queue, room_id=room_id)

@main.route('/upvote/<int:room_id>/<string:song_id>')
@login_required
def upvote(room_id,song_id):
    current_room = Room.query.get(room_id)
    queue = get_queue_as_list(current_room.queue)
    for song in queue:
        if song['id'] == song_id:
            song['votes'] += 1
            break
    current_room.queue = json.dumps(queue)
    db.session.commit()
    return redirect(url_for('main.room',room_id=room_id))

@main.route('/downvote/<int:room_id>/<string:song_id>')
@login_required
def downvote(room_id,song_id):
    current_room = Room.query.get(room_id)
    queue = get_queue_as_list(current_room.queue)
    for song in queue:
        if song['id'] == song_id:
            song['votes'] -= 1
            break
    current_room.queue = json.dumps(queue)
    db.session.commit()
    return redirect(url_for('main.room',room_id=room_id))
