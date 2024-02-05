import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from argparse import ArgumentParser

import sys
sys.path.insert(0, os.getcwd())
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

# needed premisions for each user
scope = 'user-top-read user-read-recently-played playlist-read-private'

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-q", "--quantity", dest="quantity",
                        help="Number of items to retrieve", required=True)
    args = parser.parse_args()
    quantity = int(args.quantity)

    user = User("test")
    top = user.getTopTracks(es, scope, limit=quantity, time_range='short_term')
    
    print("TOP TRACKS: ")
    for track in top:
        print("-", track.name)
    print()

    print("USER METAVECTOR: ")
    print(user.metadataVector)
    print()

    print("ARTISTS: ", set(user.artists))
    print()

    print("* User populated")
    es.insertUser(user)    