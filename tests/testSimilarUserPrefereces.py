"""
This script is used to test the similarity of user preferences.
"""

import os
from dotenv import load_dotenv
import numpy as  np
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from argparse import ArgumentParser

import sys
sys.path.insert(0, os.getcwd())

from models.track import Track
from models.elasticLink import ElasticLink

load_dotenv()
elastic_endpoint = os.getenv("ELASTIC_HOST")
elastic_api_key = os.getenv("API_KEY")
es = ElasticLink(elastic_endpoint, elastic_api_key)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-u", "--user", dest="user",
                        help="test user",
                        default="1")
    args = parser.parse_args()
    user_id = int(args.user)

    # given that int_id of the user
    # retrieve a list of similar users
    similarUsers = es.getSimilarUsers(user_id, 10)
    print("Similar users: ", similarUsers)