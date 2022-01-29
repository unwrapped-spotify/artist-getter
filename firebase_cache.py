from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin
from spotipy import CacheHandler

class FirestoreCacheHandler(CacheHandler):
    def __init__(self, doc_ref):
        self.doc_ref = doc_ref
    
    def get_cached_token(self):
        return(self.doc_ref.get(field_paths = ['token']).to_dict()['token'])
    
    def save_token_to_cache(self, token_info):
        self.doc_ref.update({
            'token': token_info
        })
