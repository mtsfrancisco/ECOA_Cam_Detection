import os
import sys

# Add the src directory to the PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from src.firebase.user_image_manager import UserImageManager

def add_user():
    """
    Add a user to Firebase with their image converted to Base64.

    Args:
        image_name (str): The user's image file name.

    Returns:
        str: The generated user ID.
    
    """

    manager = UserImageManager()
    return manager.create_user('Space', 'Ship', 'S')


def update_user():
    """
    Update a user's data in Firebase.

    Args:
        user_id (str): The user ID.
        image_name (str): The user's image file name.

    Returns:
        dict: User data including name and image path.
    """

    manager = UserImageManager()
    return manager.update_user_data('Matheus', 'Francisco', 'M', '134612')


def delete_user():
    """
    Delete a user from Firebase.

    Args:
        user_id (str): The user ID.
    """

    manager = UserImageManager()
    return manager.delete_user('134612')

def recover_users():
    """
    Recover all users from Firebase.

    Returns:
        dict: All users in the database.
    """

    manager = UserImageManager()
    return manager.recover_users()
#print(add_user())
#print(update_user())
#print(delete_user())
print(recover_users())