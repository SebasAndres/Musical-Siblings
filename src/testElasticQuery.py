"""
Test queries to ElasticSearch
"""
import os
from dotenv import load_dotenv

import sys
sys.path.insert(0, os.getcwd())
from models.elasticLink import ElasticLink

load_dotenv()
elastic_endpoint = os.getenv("ELASTIC_HOST")
elastic_api_key = os.getenv("API_KEY")
es = ElasticLink(elastic_endpoint, elastic_api_key)

query_v1 = {
        "size": 5,
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": {
                            "match_all": {},
                        },
                        "must_not": [
                            {
                                "term": {
                                    "spotify_user_id": "Duki Fan"
                                }
                            }
                        ],
                        "should": [
                            {
                                "terms": {
                                    "artists": ["Duki"],
                                    "boost": 500
                                }
                            }
                        ]
                    }
                },
            }
        }
    }

resp = es.client.search(index="songs-metadata", body=query_v1)

print()
print(len(resp['hits']['hits']))
print(resp['hits']['hits'])