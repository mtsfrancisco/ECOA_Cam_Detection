import os
import uuid
from src.firebase.fire import add_user, get_user, update_user, delete_user, get_all_users
from src.facial_imagery.image_conversions import image_to_base64, base64_to_image

def add_user_with_image(name, image_path):
    """
    Add a user to Firebase with their image converted to Base64.
    
    Args:
        name (str): The user's name.
        image_path (str): Path to the user's image file.
    
    Returns:
        str: The generated user ID.
    """
    image_path = os.path.join(os.path.dirname(__file__), "faces", image_path)
    user_id = str(uuid.uuid4())  # Generate a unique user ID
    base64_image = image_to_base64(image_path)
    add_user(user_id, name, base64_image)
    return user_id

def get_user_image(user_id):
    """
    Retrieve a user's image from Firebase and save it to the faces folder.
    
    Args:
        user_id (str): The user ID.
    
    Returns:
        dict: User data including name and image path.
    """
    user_data = get_user(user_id)
    if user_data:
        image_name = f"{user_id}.png"
        base64_to_image(user_data['image_64'], image_name)
        return {
            'name': user_data['name'],
            'image_path': os.path.join('faces', image_name)
        }
    return None

def update_user_image(user_id, name=None, image_path=None):
    """
    Update a user's information and/or image in Firebase.
    
    Args:
        user_id (str): The user ID.
        name (str, optional): The user's new name.
        image_path (str, optional): Path to the user's new image file.
    """
    base64_image = None
    if image_path:
        image_path = os.path.join(os.path.dirname(__file__), "faces", image_path)
        base64_image = image_to_base64(image_path)
    update_user(user_id, name, base64_image)

def delete_user_with_image(user_id):
    """
    Delete a user from Firebase and remove their image from the faces folder.
    
    Args:
        user_id (str): The user ID.
    """
    delete_user(user_id)
    image_path = os.path.join('faces', f"{user_id}.png")
    if os.path.exists(image_path):
        os.remove(image_path)

def check_all_faces_in_folder():
    """
    Check whether all faces stored in Firebase are present in the faces folder.
    
    Returns:
        list: List of user IDs whose images are missing in the faces folder.
    """
    missing_images = []
    users = get_all_users()
    
    for user_id, user_data in users.items():
        image_path = os.path.join('faces', f"{user_id}.png")
        if not os.path.exists(image_path):
            missing_images.append(user_id)
    
    return missing_images