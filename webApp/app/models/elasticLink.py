from elasticsearch import Elasticsearch
import math
from .track import Track
from .user import User

class ElasticLink():
    def __init__(self, endpoint, api_key):
        self.client = Elasticsearch(endpoint, api_key=api_key)
        self.lastIndex = dict()

    def getNewIndexId(self, index_name):
        """
        Get new index integer id for elasticsearch
        """
        return self.client.count(index=index_name)['count']
         
    def existsSong(self, spotify_id):
        """
        Check if song exists in elasticsearch,
        if it exists then returns the integer id, else return None
        """
        # get number of documents stored in a index
        # if it is 0 then return False
        query = {
            "query": {
                "match": {
                    "spotify_id": spotify_id
                }
            }
        }
        resp = self.client.search(index="songs-metadata", body=query)
        if len(resp['hits']['hits']) == 0:
            return False
        return resp['hits']['hits'][0]["_source"]["int_id"]

    def existsUser(self, spotify_id):
        """
        Check if user exists in elasticsearch,
        if it exists then returns the integer id, else return None
        """
        query = {
            "query": {
                "match": {
                    "spotify_user_id": spotify_id
                }
            }
        }
        resp = self.client.search(index="users-metadata", body=query)
        if len(resp['hits']['hits']) == 0:
            return False
        return resp['hits']['hits'][0]["_id"]

    def insertSong(self, track:Track):
        songId = self.getNewIndexId('songs-metadata')
        doc = {
            "name": track.name,
            "artists": track.artists,
            "explicit": track.explicit,
            "spotify_id": track.spotify_id,
            "int_id": songId,
            'metaVector': track.getMetadataVector()
        }
        resp = self.client.index(index="songs-metadata", id=songId, body=doc)
        self.lastIndex["songs-metadata"] = songId
        return resp
    
    def insertUser(self, user, validate=True):
        if validate and self.existsUser(user.spotify_id):
            userId = self.existsUser(user.spotify_id)
            doc = {
                "doc": {
                    "artists": list(user.artists),
                    "metaVector": user.metadataVector.tolist(),
                    "photoUrl": user.photoUrl,
                    "listened": [x.spotify_id for x in user.listened]
                }
            }
            resp = self.client.update(index="users-metadata", id=userId, body=doc)
            return resp            
        userId = self.getNewIndexId('users-metadata')
        doc = {
            "spotify_user_id": user.spotify_id,
            "artists": list(user.artists),
            "metaVector": user.metadataVector.tolist(),
            "photoUrl": user.photoUrl,
            "listened": [x.spotify_id for x in user.listened]
        }
        resp = self.client.index(index="users-metadata", id=userId, body=doc)
        return resp


    def getSongMetadata(self, spotify_id):
        """
        Get song metadata from elasticsearch
        """
        query = {
            "query": {
                "match": {
                    "spotify_id": spotify_id
                }
            }
        }
        resp = self.client.search(index="songs-metadata", body=query)
        if len(resp['hits']['hits']) == 0:
            raise Exception(f"Song with spotify_id {spotify_id} not found")
        return resp['hits']['hits'][0]["_source"]
    
    def getAllTracks(self):
        """
        Get all tracks from elasticsearch
        """
        query = {
            "query": {
                "match_all": {}
            }
        }
        # scroll in elastic
        resp = self.client.search(index="songs-metadata", body=query, scroll="1m")
        sid = resp['_scroll_id']
        scroll_size = len(resp['hits']['hits'])
        tracks = []
        # pbar = tqdm.tqdm(total=scroll_size, desc=f"Getting all tracks from elasticsearch")
        while scroll_size > 0:
            tracks.extend(resp['hits']['hits'])
            resp = self.client.scroll(scroll_id=sid, scroll='1m')
            sid = resp['_scroll_id']
            scroll_size = len(resp['hits']['hits'])
            # pbar.update(scroll_size)
        return tracks
    
    def getNumUsersRegistered(self):
        """
        Get number of users registered in elasticsearch
        """
        return self.client.count(index="users-metadata")['count']
    
    def getSimilarUsersByRegion(self, user:User, m=4, f=lambda x: math.exp(-x)):
        # Check if m < N
        if len(user.listened) < m:
            raise Exception("User has not listened enough tracks")
        
        # Get all tracks in the user region
        regionTrackIds = set() 
        i = 0
        while i < m:
            track = user.listened[i]
            radiusTracks = self.get_documents_within_radius("songs-metadata", track.getMetadataVector(), f(i))
            for r in radiusTracks['hits']['hits']:
                if r['_score'] > 0:
                    regionTrackIds.add(r['_source']['spotify_id'])
            i+=1

        # Get all users that have listened to the tracks in the region
        query = {
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
                                        "spotify_user_id": user.spotify_id
                                    }
                                }
                            ],
                            "should": [
                                {
                                    "terms": {
                                        "listened": list(regionTrackIds),
                                        "boost": 300
                                    }
                                },
                                {
                                    "terms": {
                                        "artists": list(user.artists),
                                        "boost": 200
                                    }
                                }
                            ]
                        }
                    },
                }
            }
        }
        resp = self.client.search(index="users-metadata", body=query)
        return resp['hits']['hits']

    def get_documents_within_radius(self, index, vector, radius):
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": {
                                "match_all": {},
                            }
                        }
                    },
                    "functions": [
                        {
                            "script_score": {
                                "script": {
                                    "source": "l2norm(params.queryVector, 'metaVector') > params.radius ? 0 : 1 / (l1norm(params.queryVector, 'metaVector') + 1)",
                                    "params": {
                                        "queryVector": vector,
                                        "radius": radius
                                    }
                                }
                            }
                        }
                    ]                                       
                }
            }
        }
        resp = self.client.search(index=index, body=query)
        return resp