from elasticsearch import Elasticsearch
from dotenv import load_dotenv
load_dotenv()
import os

endpoint = os.getenv("ELASTIC_HOST")
api_key = os.getenv("API_KEY")

client = Elasticsearch(endpoint, api_key=api_key)

F = 10 # Vector Colaborative Filtering Dimension
M = 14 # Vector Content Based Dimension

try:
    # client.indices.delete(index="songs-metadata")
    client.indices.delete(index="users-metadata")
    print("Indices deleted successfully")
except Exception as e:
    print(e)

usersBody = {
    "mappings": {
        "properties": {
            "spotify_user_id": {
                "type": "keyword"
            },
            "metaVector": {
                "type": "dense_vector",
                "dims": M
            },
            "artists": {
                "type": "keyword"
            },
            "photoUrl": {
                "type": "keyword"
            },
            "listened": {
                "type": "keyword"
            }
        }
    }
}
client.indices.create(index="users-metadata", body=usersBody)
print("Users index created successfully")

"""
songsBody = {
    "mappings": {
        "properties": {
            "name": {
                "type": "keyword"
            },
            "artists": {
                "type": "keyword"
            },
            "explicit": {
                "type": "boolean"
            },
            "spotify_id": {
                "type": "keyword"
            },
            "int_id": {
                "type": "integer"
            },
            "metaVector": {
                "type": "dense_vector",
                "dims": M
            }
        }
    }
}
client.indices.create(index="songs-metadata", body=songsBody)
print("Songs index created successfully")
"""