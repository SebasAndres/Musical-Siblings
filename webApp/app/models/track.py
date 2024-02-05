class Track:
    def __init__(self, track_metadata={}, spotify_id=None, es=None):
        if spotify_id:
            # we need an ElasticLink object to load track metadata
            if not es:
                raise Exception("No elasticsearch link provided")            
  
            # load track metadata from elasticsearch
            track_metadata = es.getSongMetadata(spotify_id)    
            self.artists = track_metadata['artists']
            self.name = track_metadata['name']
            self.explicit = track_metadata['explicit']
            self.spotify_id = track_metadata['spotify_id']
            self.integer_id = track_metadata['int_id']       

            # load audio features from elasticsearch
            self.danceability = track_metadata['metaVector'][0]
            self.energy = track_metadata['metaVector'][1]
            self.key = track_metadata['metaVector'][2]
            self.loudness = track_metadata['metaVector'][3]
            self.mode = track_metadata['metaVector'][4]
            self.speechiness = track_metadata['metaVector'][5]
            self.acousticness = track_metadata['metaVector'][6]
            self.instrumentalness = track_metadata['metaVector'][7]
            self.liveness = track_metadata['metaVector'][8]
            self.valence = track_metadata['metaVector'][9]
            self.tempo = track_metadata['metaVector'][10]*100
            self.duration_ms = track_metadata['metaVector'][11]*100000
            self.time_signature = track_metadata['metaVector'][12]
            self.popularity = track_metadata['metaVector'][13]*100

            return

        # load data from track_metadata parameter    
        self.name = track_metadata['name']
        self.artists = [a['name'] for a in track_metadata['artists']]
        self.explicit = track_metadata['explicit']
        self.spotify_id = track_metadata['id']
        self.popularity = track_metadata['popularity']  
        self.integer_id = None

    def setAudioFeatures(self, audio_features):
        self.danceability = audio_features['danceability']
        self.energy = audio_features['energy']
        self.key = audio_features['key']
        self.loudness = audio_features['loudness']
        self.mode = audio_features['mode']
        self.speechiness = audio_features['speechiness']
        self.acousticness = audio_features['acousticness']
        self.instrumentalness = audio_features['instrumentalness']
        self.liveness = audio_features['liveness']
        self.valence = audio_features['valence']
        self.tempo = audio_features['tempo']
        self.duration_ms = audio_features['duration_ms']
        self.time_signature = audio_features['time_signature']

    def setIntegerId(self, id):
        self.integer_id = id

    def getMetadataVector(self):
        return [self.danceability, self.energy, self.key,
                self.loudness, self.mode, self.speechiness,
                self.acousticness, self.instrumentalness,
                self.liveness, self.valence, self.tempo/100,
                self.duration_ms/100000, self.time_signature,
                self.popularity/100]