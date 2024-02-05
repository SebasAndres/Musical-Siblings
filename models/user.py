import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from models.track import Track

class User:
    def __init__(self, user_id="", spotifyData=None):
        self.spotify_id = user_id
        self.photoUrl = ""
        if spotifyData:
            self.spotify_id = spotifyData['id']
            self.photoUrl = spotifyData['images'][0]['url']
        self.artists = set() # top artists listened
        self.metadataVector = None # user metadata vector
        self.listened = []  # top tracks listened
        self.metaCluster = None # cluster to which the user belongs

    def getTopTracks(self, es, scope:str, limit=30, time_range='short_term'):
        """
        Get user's top tracks from Spotify Web Api,
        It also sets the user's metadataVector and their topArtistsListened set

        If the songs are not registered in MusicalMatch ElasticSearch,
        then they are registered and their metadataVector is read and set through
        the another Spotify Web api call
        """
        username = ""
        token = util.prompt_for_user_token(username, scope)
        try:
            sp = spotipy.Spotify(auth=token)
        except Exception as e:
            print(e)
            return

        # get top tracks from spotify api
        top_tracks = sp.current_user_top_tracks(limit=limit, offset=0, time_range=time_range)        
        track_ids_to_populate = [] # songs to insert in elastic
        track_id_n_order = dict() # track id and order in top tracks
        sorted_resp = np.empty(limit, dtype=object) # sorted response

        # we ll first check if the song is already in elastic
        # if it is, then we ll get the metadataVector from elastic
        # else we ll get the metadataVector from spotify api altogether in one api call
        for i, track_meta in enumerate(top_tracks['items']):
            track_id_n_order[track_meta['id']] = i
            if es.existsSong(track_meta['id']):
                track = Track(spotify_id=track_meta['id'])   
                sorted_resp[i] = track                
            else:
                track = Track(track_metadata=track_meta)
                track_ids_to_populate.append(track.spotify_id)
                sorted_resp[i] = track  
            track_ids_to_populate.append(track.spotify_id)
            # we ll also get the artists from the top tracks
            for artist in track.artists:
                self.artists.add(artist)

        # we populate the songs that were not already in Elastic
        # to do that, we have to get the audio features from spotify api
        tracks_features = sp.audio_features(track_ids_to_populate)
        for feature in tracks_features:
            track_id = feature['id']
            respIndex = track_id_n_order[track_id]
            sorted_resp[respIndex].setAudioFeatures(feature)
        
        # set user metadataVector
        self.metadataVector = np.mean([track.getMetadataVector() for track in sorted_resp], axis=0)            

        return sorted_resp
    
    def getId(self):
        return self.id

    def getUserVectorCL(self):
        """ Vector por Filtrado Colaborativo """
        return []
    
    def getUserVectorFromListened(self):
        """ Vector media de los vectores de canciones escuchadas """
        songMatrix = []
        for j, song in enumerate(self.listened):
            songMatrix.append(np.array(song.getMetadataVector())/(1+j*0.01))
        self.metadataVector = np.mean(songMatrix, axis=0)
        return self.metadataVector
    
    def listenTrack(self, spotify_id, es=None):
        track = Track(spotify_id=spotify_id, es=es)
        self.listened.append(track)
        for artist in track.artists:
            self.artists.add(artist)

    def setMetaCluster(self, cluster):
        self.metaCluster = cluster