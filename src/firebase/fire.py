import firebase_admin
import os
from firebase_admin import credentials, db

# Get the service account key from the Firebase project settings
# Gear icon > Project settings > Service accounts > Generate new private key
# Save the file in the same directory as this file > Filename: serviceAccountKey.json


class FirebaseManager:
    '''
    Class to manage Firebase operations.
    --- Do not touch anything in this file ---
    -> Also good to look into this file to see ...
    -> ... what functionalities exist
    YES ENZO I TOUCHED THE FILE, I NEEDED TO CREATE A VERIFICATION TO CHECK IF THE APP WAS BEEING CALLED MORE THAN ONCE, DEAL WITH IT, I DONT CARE
    '''
    class FirebaseManager:
        def __init__(self):
            if not firebase_admin._apps:
                service_account_path = os.path.join(
                    os.path.dirname(__file__), 'serviceAccountKey.json')
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://ecoa-camera-default-rtdb.firebaseio.com' 
            })

    def add_user(self, user_id, user_data):
        ref = db.reference(f'users/{user_id}')
        ref.set(user_data)

    def get_user(self, user_id):
        ref = db.reference(f'users/{user_id}')
        return ref.get()

    def update_user(self, user_id, user_data):
        ref = db.reference(f'users/{user_id}')
        ref.update(user_data)

    def delete_user(self, user_id):
        ref = db.reference(f'users/{user_id}')
        ref.delete()

    def get_all_users(self):
        ref = db.reference('users')
        return ref.get()
    
    def add_history(self, user_id, history_data):
        try:
            ref = db.reference(f'history/{user_id}')
            new_history_ref = ref.push()
            new_history_ref.set(history_data)
            return True
        except Exception as e:
            print(f"An error occurred while adding history: {e}")
            return False

    def get_user_history(self, user_id):
        try:
            ref = db.reference(f'history/{user_id}')
            history = ref.get()
            return history
        except Exception as e:
            print(f"An error occurred while retrieving history: {e}")
            return None

    def delete_user_history(self, user_id):
        try:
            ref = db.reference(f'history/{user_id}')
            ref.delete()
            return True
        except Exception as e:
            print(f"An error occurred while deleting history: {e}")
            return False