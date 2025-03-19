import firebase_admin
import os
from firebase_admin import credentials, db

# Get the service account key from the Firebase project settings
# Gear icon > Project settings > Service accounts > Generate new private key
# Save the file in the same directory as this file > Filename: serviceAccountKey.json


class FirebaseManager:
    '''
    Class to manage Firebase operations.
    '''
    def __init__(self):
        if not firebase_admin._apps:
            service_account_path = os.path.join(
                os.path.dirname(__file__), 'serviceAccountKey.json')
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://ecoa-camera-default-rtdb.firebaseio.com'
            })

    def add_user(self, user_id, user_data):
        '''
        Adds a new user to the Firebase database.
        
        Parameters:
        user_id (str): The ID of the user.
        user_data (dict): A dictionary containing user data.
        '''
        ref = db.reference(f'users/{user_id}')
        ref.set(user_data)

    def get_user(self, user_id):
        '''
        Retrieves a user from the Firebase database.
        
        Parameters:
        user_id (str): The ID of the user.
        
        Returns:
        dict: A dictionary containing user data.
        '''
        ref = db.reference(f'users/{user_id}')
        return ref.get()

    def update_user(self, user_id, user_data):
        '''
        Updates an existing user in the Firebase database.
        
        Parameters:
        user_id (str): The ID of the user.
        user_data (dict): A dictionary containing updated user data.
        '''
        ref = db.reference(f'users/{user_id}')
        ref.update(user_data)

    def delete_user(self, user_id):
        '''
        Deletes a user from the Firebase database.
        
        Parameters:
        user_id (str): The ID of the user.
        '''
        ref = db.reference(f'users/{user_id}')
        ref.delete()

    def get_all_users(self):
        '''
        Retrieves all users from the Firebase database.
        
        Returns:
        dict: A dictionary containing all users data.
        '''
        ref = db.reference('users')
        return ref.get()
    
    def add_history(self, user_id, history_data):
        '''
        Adds a history entry for a user in the Firebase database.
        
        Parameters:
        user_id (str): The ID of the user.
        history_data (dict): A dictionary containing history data.
        
        Returns:
        bool: True if the operation was successful, False otherwise.
        '''
        try:
            ref = db.reference(f'history/{user_id}')
            new_history_ref = ref.push()
            new_history_ref.set(history_data)
            return True
        except Exception as e:
            print(f"An error occurred while adding history: {e}")
            return False

    def get_user_history(self, user_id):
        '''
        Retrieves the history of a user from the Firebase database.
        
        Parameters:
        user_id (str): The ID of the user.
        
        Returns:
        dict: A dictionary containing the user's history data, or None if an error occurred.
        '''
        try:
            ref = db.reference(f'history/{user_id}')
            history = ref.get()
            return history
        except Exception as e:
            print(f"An error occurred while retrieving history: {e}")
            return None
        
    def get_all_history(self):
        '''
        Retrieves all history entries from the Firebase database.
        
        Returns:
        dict: A dictionary containing all history entries, or None if an error occurred.
        '''
        try:
            ref = db.reference('history')
            history = ref.get()
            return history
        except Exception as e:
            print(f"An error occurred while retrieving history: {e}")
            return

    def delete_user_history(self, user_id):
        '''
        Deletes the history of a user from the Firebase database.
        
        Parameters:
        user_id (str): The ID of the user.
        
        Returns:
        bool: True if the operation was successful, False otherwise.
        '''
        try:
            ref = db.reference(f'history/{user_id}')
            ref.delete()
            return True
        except Exception as e:
            print(f"An error occurred while deleting history: {e}")
            return False