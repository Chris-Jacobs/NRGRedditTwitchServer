from flask import Flask
from flask import request
import streams
import json
from threading import Thread
from time import sleep
import requests
import datetime
import sys
app = Flask(__name__)



sleepTime = 15
discordURL = streams.keys['StreamsWebhook']
oldStreams = []
lastUpdated = None
@app.route('/info', methods = ['GET'])
def info():
    user = request.args.get('user')
    return json.dumps(streams.getStream(user))
@app.route("/follow", methods = ['GET', 'POST'])
def follow():
    if request.method == 'GET':
        follows = list(streams.getFollows(name = True))
        js = json.dumps(follows)
        return js
    elif request.method == 'POST':
        data = request.json
        username = data['username']
        print(username)
        return streams.follow(username)

@app.route("/unfollow", methods = ['POST'])
def unfollow():
    data = request.json
    username = data['username']
    print(username)
    return streams.unfollow(username)

@app.route("/live", methods = ['GET'])
def live():
    liveStreams = []
    totalViewers = 0
    for stream in oldStreams:
        data = {}
        data['game'] = streams.lookupGame(stream['game_id'])
        data['name'] = streams.getUsername(stream['user_id'])
        data['title'] = stream['title']
        data['viewers'] = stream['viewer_count']
        totalViewers += int(data['viewers'])
        liveStreams.append(data)
    print(liveStreams)
    liveStreams.sort(key = lambda s: int(s['viewers']), reverse = True)
    return json.dumps({"streams": liveStreams, "total_viewers": totalViewers, "time": lastUpdated.strftime("%Y-%m-%d %H:%M:%S")})
        
def messageDiscord(newStreams):
    for stream in newStreams:
        if stream.strip() == "":
            continue
        msg  = "{stream} is now live!\nhttp://twitch.tv/{stream}".format(stream = stream)
        requests.post(discordURL, json = {"content": msg})
def getStreams():
    global oldStreams, lastUpdated
    oldStreams = streams.getLive(streams.getFollows())
    lastUpdated = datetime.datetime.now()
    while True:
        try:
            sleep(sleepTime)
            try:
                newStreams = streams.getLive(streams.getFollows())
            except Exception:
                print('Error getting new streams')
                print(sys.exc_info()[0])
                print(sys.exc_info()[1])
                newStreams = oldStreams
            newLiveStreams = compare(oldStreams, newStreams)
            oldStreams = newStreams
            lastUpdated = datetime.datetime.now()
            messageDiscord(newLiveStreams)
        except Exception:
            print('Unknown Error')
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

def compare(oldStreams, newStreams):
    o = getUsernames(oldStreams)
    n = getUsernames(newStreams)
    return (n.difference(o))

def getUsernames(streamData):
    s = set()
    for stream in streamData:
        try:
            s.add(streams.getUsername(stream['user_id']))
        except KeyError:
            print('Error getting username')
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            s.add(stream['user_name'])
    return s

t = Thread(target=getStreams, daemon=True)
t.start()
app.run(debug=False, port = 5001)
