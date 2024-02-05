"""
Reads and inserts songs from an artist to elasticsearch
It includes the audio features from Spotify Web Api
"""

import os
from dotenv import load_dotenv
import tqdm
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from argparse import ArgumentParser
import time

import sys
sys.path.insert(0, os.getcwd())

from models.track import Track
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

def insertArtistSongs(artist_name, lim=20):
    """
    Insert artist songs to elasticsearch:
    """
    # get track ids from artists
    results = sp.search(q=f'artist:{artist_name}', type='track', limit=lim)
    track_ids = []
    artist_tracks = []
    pbar = tqdm.tqdm(total=len(results['tracks']['items']),
                     desc=f"Validating songs with Elastic")
    for track_meta in results['tracks']['items']:
        track = Track(track_metadata=track_meta)
        # only tracks that are not already in elasticsearch
        if not es.existsSong(track.spotify_id):
            track_ids.append(track.spotify_id)    
            artist_tracks.append(track)
        pbar.update(1)
    pbar.close()

    # get audio_features from Spotify Api 
    # insert vector to Track object
    tracks_features = sp.audio_features(track_ids)
    pbar = tqdm.tqdm(total=len(artist_tracks), desc=f"Inserting {artist_name} songs to elasticsearch")
    for i, track in enumerate(artist_tracks):
        if tracks_features[i] is None:
            pbar.update(1)
            continue
        
        track.setAudioFeatures(tracks_features[i])
        es.insertSong(track)
        
        # some sleep time to let ElasticSearch process the request
        time.sleep(0.1)
        pbar.update(1)
    pbar.close()
    return 

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-a', '--artist', help='Artist name', required=True)
    parser.add_argument('-l', '--limit', help='Number of songs to insert', required=False)
    args = parser.parse_args()

    artist_name = args.artist
    lim = args.limit
    insertArtistSongs(artist_name, lim)
