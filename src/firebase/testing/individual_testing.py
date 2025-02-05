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
    return manager.create_user('Matheus', 'Franciso', 'M', '134612')



def get_user(user_id):
    """
    Retrieve a user's image from Firebase and save it to the faces folder.

    Args:
        user_id (str): The user ID.

    Returns:
        dict: User data including name and image path.
    """

    manager = UserImageManager()
    return manager.get_user_image(user_id)

def add_user_local(name, user_id):
    """
    Add user lcally

    Args:
        user_id (str): The user ID.
        name (str): The user's name.

    Returns:
        dict: User data including name and image path.
    """

    manager = UserImageManager()
    manager.add_user_local(name, user_id)
    return manager.add_user_with_image(user_id, f"{name}.jpg")

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
    return manager.update_user_data('Matheus', 'Francisco', 'M', 134612)

print(add_user())
#print(add_user("Matheus.jpg"))