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

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--username", dest='username', 
                        help="Spotify username", default='', required=False)
    args = parser.parse_args()
    username = args.username

    scope = 'user-read-private'
    token = util.prompt_for_user_token(username,
                                       scope,
                                       client_id=spotify_client_id, 
                                       client_secret=spotify_client_secret,
                                       redirect_uri='http://localhost:8888/callback')
    sp = spotipy.Spotify(auth=token)
    userSpotifyData = sp.current_user()
    user = User(spotifyData=userSpotifyData) 
    print("Spotify USER ID: ", user.spotify_id)