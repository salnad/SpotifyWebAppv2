import json

def add_dict_to_queue(dict, queueStr):
    queue = json.loads(queueStr)
    queue.append(dict)
    return json.dumps(queue)


jsonString = "[]"

dictOne = {'id': '2xLMifQCjDGFmkHkpNLD9h', 'votes': 0, 'track_uri': 'spotify:track:2xLMifQCjDGFmkHkpNLD9h', 'artists': ['Travis Scott'], 'track_title': 'SICKO MODE'}
dictTwo = {'id': '75ls0gurX68lUmMjE7QcsE', 'votes': 0, 'track_uri': 'spotify:track:75ls0gurX68lUmMjE7QcsE', 'artists': ['Jeremy Zucker'], 'track_title': 'all the kids are depressed'}

arr = json.loads(jsonString)
arr.append(dict)
jsonString = json.dumps(arr)

print(jsonString)
