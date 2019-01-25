import requests
import json
with open('keys.json') as f:
    keys = json.load(f)
client_id = keys['TwitchClientID']
base_url = 'https://api.twitch.tv/helix/'
headers = {'Accept' : 'application/vnd.twitchtv.v5+json', 'Client-ID' :client_id}
accessCode = keys['TwitchAccessCode']
client_secret = keys['TwitchClientSecret']
access_token = keys['TwitchAccessToken']
refresh_token = keys['TwitchRefreshToken']
twitchId = keys['TwitchID']
gameMap = {}

def lookupGame(id):
    global gameMap
    if id not in gameMap:
        url = base_url + 'games?id={id}'.format(id = id)
        r = requests.get(url, headers = headers).json()
        gameMap[id] = r['data'][0]['name']
    return gameMap[id]


def getToken():
    global access_token, refresh_token
    url = "https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&code={access_code}&grant_type=authorization_code&redirect_uri=http://localhost".format(client_id = client_id, client_secret = client_secret, access_code = accessCode)
    print(url)
    r = requests.post(url).json()
    print(r)
def refreshToken():
    url = "https://id.twitch.tv/oauth2/token--data-urlencode?grant_type=refresh_token&refresh_token={refreshToken}&client_id={client_id}&client_secret={client_secret}".format(client_id = client_id, client_secret = client_secret, refreshToken = refresh_token)
    print(url)
    r = requests.post(url).json()
    print(r)
def getID(username):
    url = "https://api.twitch.tv/kraken/users?login={username}".format(username = username)
    response = requests.get(url, headers=headers).json()
    id = response['users'][0]['_id']
    return id
def follow(username):
    url = "https://api.twitch.tv/kraken/users/{userid}/follows/channels/{channelid}".format(userid = twitchId, channelid = getID(username))
    followHeaders = headers.copy()
    followHeaders['Authorization'] = "OAuth " + access_token
    r = requests.put(url, headers= followHeaders)
    print(r.reason)
    return r.reason

def unfollow(username):
    url = "https://api.twitch.tv/kraken/users/{userid}/follows/channels/{channelid}".format(userid = twitchId, channelid = getID(username))
    followHeaders = headers.copy()
    followHeaders['Authorization'] = "OAuth " + access_token
    r = requests.delete(url, headers= followHeaders)
    print(r.reason)
    return r.reason
def getFollows(name = False):
    params = { 'from_id': twitchId, 'first': 100}
    url = base_url + 'users/follows'

    response = requests.get(url, params=params, headers=headers).json()
    follows = []
    while len(response['data']) > 0:
        follows += response['data']
        params.update({ 'after': response['pagination']['cursor'] })
        response = requests.get(url, params=params, headers=headers).json()


    return (f['to_name'] for f in follows) if name else (f['to_id'] for f in follows)

def getLive(follows):
    url = base_url + 'streams'
    params = [ ('user_id', str(user_id)) for user_id in follows ]
    response = requests.get(url, params=params, headers=headers).json()
    return response['data']
