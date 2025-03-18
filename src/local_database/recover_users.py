import sys
import os
import sys
import os

# Add the src directory to the PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from src.firebase.user_image_manager import UserImageManager

print("imported")

def recover_users():
    """
    Recover all users from Firebase.

    Returns:
        dict: All users in the database.
    """
    print("Starting")

    manager = UserImageManager()

    print("Manager initiated")

    return manager.recover_users()

print(recover_users())