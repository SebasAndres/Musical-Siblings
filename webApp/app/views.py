from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

import os
from dotenv import load_dotenv
load_dotenv()

from .models import ElasticLink
from .models import User

def index(request):
    # .env file
    elastic_endpoint = os.getenv("ELASTIC_HOST")
    elastic_api_key = os.getenv("API_KEY")

    # elasticsearch link 
    es = ElasticLink(elastic_endpoint, elastic_api_key)

    # number of users registered in app
    numUsersRegistered = es.getNumUsersRegistered()

    context = {
        'num_users_registered': numUsersRegistered
    }

    return render(request, 'index.html', context)

def getSimilarUsersByMeta(request, user_id):
    # .env file
    elastic_endpoint = os.getenv("ELASTIC_HOST")
    elastic_api_key = os.getenv("API_KEY")
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    # elasticsearch link 
    es = ElasticLink(elastic_endpoint, elastic_api_key)

    # spotify
    spotifyCredentials = {
        'id': spotify_client_id,
        'secret': spotify_client_secret,
        'redirect_uri': 'http://127.0.0.1:8888/callback'
    }


    # get user's credentials
    username = ""
    token = util.prompt_for_user_token(username,
                                        'user-top-read user-read-private',
                                        client_id=spotifyCredentials['id'],
                                        client_secret=spotifyCredentials['secret'],
                                        redirect_uri=spotifyCredentials['redirect_uri'])
    try:
        sp = spotipy.Spotify(auth=token)
    except Exception as e:
        print(e)
        return

    userSpotifyData = sp.current_user()
    user = User(spotifyData=userSpotifyData) 
    top = user.getTopTracks(es, sp, limit=20, time_range='short_term')

    if not es.existsUser(user.spotify_id):
        es.insertUser(user)

    similarUsers = es.getSimilarUsersByRegion(user)
    
    resp = []
    for rcm_user in similarUsers:
        userIG = rcm_user["_source"]['spotify_user_id']
        score = rcm_user["_score"]
        commonArtists = set(rcm_user["_source"]['artists']).intersection(user.artists)
        resp.append((userIG, score, commonArtists))

    return HttpResponse("<br>".join([str(t) for t in resp]))