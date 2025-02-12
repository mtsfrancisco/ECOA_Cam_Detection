import os
import shutil
import random
import json
from src.firebase.fire import FirebaseManager

class HistoryManager:
    def __init__(self):
        self.firebase_manager = FirebaseManager()

    def add_history(self, user_id, history_data):
        '''
        Add a history to Firebase.

        Args:
            user_id (str): The user ID.
            history_data (dict): The history data.
            -> history_data should contain the following
                - date (str): The date of the history.
                - time (str): The time of the history.
                - status (str): Entering/Leaving.
        
        Returns:
            str: Message indicating that the history was added successfully.
        '''

        # When questioning whether or not the code should really
        # have yet another file with the same function, name, and parameters
        # it's important to consider what was reasearched called the ... 
        # ... Single Responsibility Principle and also note that we want to only
        # reference the certificate a singular time within the codebase
        self.firebase_manager.add_history(user_id, history_data)

    def get_user_history(self, user_id):
        '''
        Get the history of a user from Firebase.

        Args:
            user_id (str): The user ID.
        
        Returns:
            dict: The history of the user.
        '''

        return self.firebase_manager.get_user_history(user_id)
    
    def delete_user_history(self, user_id):
        '''
        Delete all history of a user from Firebase.
        -> Should only be used for TESTING PURPOSES

        Args:
            user_id (str): The user ID.

        Returns:
            str: Message indicating that the history was deleted successfully.
        '''

        self.firebase_manager.delete_user_history(user_id)
