import os
import shutil
import random
import json
from .fire import FirebaseManager

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
                - id (str): The ID of the person.
                - name (str): The name of the person.
                - date (str): The date of the history.
                - time (str): The time of the history.
                - status (str): Entering/Leaving.
        
        Returns:
            str: Message indicating whether the history was added successfully.
        '''
        success = self.firebase_manager.add_history(user_id, history_data)
        if success:
            return "History added successfully"
        else:
            return "Failed to add history"

    def get_user_history(self, user_id):
        '''
        Get the history of a user from Firebase.

        Args:
            user_id (str): The user ID.
        
        Returns:
            dict: The history of the user, or a message indicating failure.
        '''
        history = self.firebase_manager.get_user_history(user_id)
        if history is not None:
            return history
        else:
            return "Failed to retrieve history"
        
    def get_all_history(self):
        '''
        Get all history from Firebase.

        Returns:
            dict: All history, or a message indicating failure.
        '''
        history = self.firebase_manager.get_all_history()
        if history is not None:
            return history
        else:
            return "Failed to retrieve history"

    def delete_user_history(self, user_id):
        '''
        Delete all history of a user from Firebase.
        -> Should only be used for TESTING PURPOSES

        Args:
            user_id (str): The user ID.

        Returns:
            str: Message indicating whether the history was deleted successfully.
        '''
        success = self.firebase_manager.delete_user_history(user_id)
        if success:
            return "History deleted successfully"
        else:
            return "Failed to delete history"