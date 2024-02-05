import os
from dotenv import load_dotenv
import tqdm
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from argparse import ArgumentParser

import sys
sys.path.insert(0, os.getcwd())

from models.track import Track
from models.user import User
from models.elasticLink import ElasticLink

load_dotenv()
elastic_endpoint = os.getenv("ELASTIC_HOST")
elastic_api_key = os.getenv("API_KEY")
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# elasticsearch link 
es = ElasticLink(elastic_endpoint, elastic_api_key)

# spotify
os.environ["SPOTIPY_CLIENT_ID"] = spotify_client_id
os.environ["SPOTIPY_CLIENT_SECRET"] = spotify_client_secret
os.environ['SPOTIPY_REDIRECT_URI']='http://localhost:8888/callback'
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret) 
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def getAllTracksInElastic():
    songsByArtist = dict() # artist -> {song_name: song_id}
    allTracks = [] # list of all tracks
    registered = set() # set of all track ids already registered
    tracks = es.getAllTracks()
    for resp in tracks:
        track_meta = resp["_source"]
        track_id = track_meta["spotify_id"]                       
        if track_id not in registered:
            track = Track(sp, track_id, es)
            allTracks.append(track)
            registered.add(track_id)
        for artist in track_meta["artists"]:
            if artist not in songsByArtist:
                songsByArtist[artist] = dict()
            songsByArtist[artist].update({track_meta["name"]: track_id})
    
    return songsByArtist, allTracks

def getTestUsers():

    songsByArtist, allTracks = getAllTracksInElastic()
    
    # house listener user
    usr0 = User('House fan')
    usr0.listenTrack(songsByArtist["Diplo"]["Be Right There"], es=es)
    usr0.listenTrack(songsByArtist["Diplo"]["On My Mind"], es=es)

    # trap ARG listener user
    usr1 = User('Duki Fan')
    usr1.listenTrack(songsByArtist["Duki"]["Rockstar"], es=es)
    usr1.listenTrack(songsByArtist["Duki"]["Si Me Sobrara el Tiempo"], es=es)
    usr1.listenTrack(songsByArtist["YSY A"]["CUÁNTO VALE HACER EL AMOR?"], es=es)

    # pop ARG listener user
    usr2 = User('Emilia Fan') 
    usr2.listenTrack(songsByArtist["Emilia"]["GTA.mp3"], es=es)
    usr2.listenTrack(songsByArtist["Emilia"]["La_Original.mp3"], es=es)
    usr2.listenTrack(songsByArtist["TINI"]["La_Original.mp3"], es=es)

    # pop USA listener user
    usr3 = User('Taylor Swift Fan')
    usr3.listenTrack(songsByArtist["Taylor Swift"]["All Too Well (10 Minute Version) (Taylor's Version) (From The Vault)"], es=es)
    usr3.listenTrack(songsByArtist["Taylor Swift"]["Karma"], es=es)
    usr3.listenTrack(songsByArtist["Taylor Swift"]["Lover"], es=es)

    # pop USA listener user
    usr4 = User('The 1975 Fan')
    usr4.listenTrack(songsByArtist["The 1975"]["Robbers"], es=es)
    usr4.listenTrack(songsByArtist["The 1975"]["Happiness"], es=es)
    usr4.listenTrack(songsByArtist["The 1975"]["It's Not Living (If It's Not With You)"], es=es)
    usr4.listenTrack(songsByArtist["The 1975"]["I Always Wanna Die (Sometimes)"], es=es)

    # pop USA and ARG listener
    usr5 = User('Taylor Swift and Emilia Fan')
    usr5.listenTrack(songsByArtist["Taylor Swift"]["All Too Well (10 Minute Version) (Taylor's Version) (From The Vault)"], es=es)
    usr5.listenTrack(songsByArtist["Taylor Swift"]["Karma"], es=es)
    usr5.listenTrack(songsByArtist["Emilia"]["La_Original.mp3"], es=es)
    usr5.listenTrack(songsByArtist["Emilia"]["como si no importara"], es=es)
    usr5.listenTrack(songsByArtist["Nicki Nicole"]["CAMBIANDO LA PIEL"], es=es)

    # The 1975 and Taylor Swift listener
    usr6 = User('The 1975 and Taylor Swift Fan')
    usr6.listenTrack(songsByArtist["Taylor Swift"]["All Too Well (10 Minute Version) (Taylor's Version) (From The Vault)"], es=es)
    usr6.listenTrack(songsByArtist["Taylor Swift"]["Karma"], es=es)
    usr6.listenTrack(songsByArtist["The 1975"]["Robbers"], es=es)
    usr6.listenTrack(songsByArtist["The 1975"]["Happiness"], es=es)

    # Skrillex fan
    usr7 = User('Skrillex Fan')
    usr7.listenTrack(songsByArtist["Skrillex"]['Rumble'], es=es)
    usr7.listenTrack(songsByArtist["Skrillex"]['Fine Day Anthem'], es=es)
    usr7.listenTrack(songsByArtist["Skrillex"]['Leave Me Like This'], es=es)

    testUsers = [usr0, usr1, usr2, usr3, usr4, usr5, usr6, usr7]
    return testUsers, allTracks, songsByArtist