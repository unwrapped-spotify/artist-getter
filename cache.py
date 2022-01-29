from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin

class FirestoreCacheHandler():
    def __init__(self, user, project_id):
        cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred, {
            'projectId': project_id
        })
        
        db = firestore.client()
        self.doc_ref = db.collection('users').document(user)
    
    def get_cached_token(self):
        return(self.doc_ref.get(field_paths = ['token']).to_dict()['token'])
    
    def save_token_to_cache(self, token_info):
        self.doc_ref.update({
            'token': token_info
        })
