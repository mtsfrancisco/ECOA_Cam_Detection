import os
import sys

# Add the src directory to the PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from src.facial_imagery.user_image_manager import UserImageManager

def add_user(image_name):
    """
    Add a user to Firebase with their image converted to Base64.

    Args:
        image_name (str): The user's image file name.

    Returns:
        str: The generated user ID.
    
    """

    manager = UserImageManager()
    return manager.add_user_with_image(image_name)


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
    return manager.add_user_local(name, user_id)


print(add_user_local("Matheus", "23461"))
print(add_user("Matheus.jpg"))