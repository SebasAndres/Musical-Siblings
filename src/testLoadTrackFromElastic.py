"""
Get metadata information from a track stored in ElasticSearch
"""
import os
from dotenv import load_dotenv
from argparse import ArgumentParser

import sys
sys.path.insert(0, os.getcwd())
from models.elasticLink import ElasticLink
from models.track import Track

load_dotenv()
elastic_endpoint = os.getenv("ELASTIC_HOST")
elastic_api_key = os.getenv("API_KEY")
es = ElasticLink(elastic_endpoint, elastic_api_key)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--id", dest="id",
                        help="Spotify id of the track", 
                        default='6y6xhAgZjvxy5kR5rigpY3')
    args = parser.parse_args()
    track = Track(spotify_id=args.id, es=es)
    print("Track name: ", track.name)
    print("Artists: ", list(track.artists))
    print("Explicit: ", track.explicit)
    print("Spotify ID:", track.spotify_id)

