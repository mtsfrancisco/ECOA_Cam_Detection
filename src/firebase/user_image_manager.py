import os
import uuid
import random
import json
from src.firebase.fire import add_user, get_user, update_user, delete_user, get_all_users
from src.firebase.image_conversions import image_to_base64, base64_to_image

class UserImageManager:
    def __init__(self):
        self.users_dir = os.path.join(os.path.dirname(__file__), '..', 'local_database', 'users')

    def add_user_local(self, user_data):
        """
        Add a user to Firebase with their image stored locally.
        Used when a new user is being made
        -> There has to be an image of the user being made in the temp_user folder!!!
        
        Args:
            name (str): The user's name.
            user_id (str, optional): The user ID.
        
        Returns:
            str: The generated user ID.
        """
        
        temp_dir = os.path.abspath(os.path.join(self.users_dir, '..', 'temp_user'))
        image_filename = self._find_first_image(temp_dir)
        
        if image_filename:
            original_image_path = os.path.join(temp_dir, image_filename)
            new_image_name = f"{user_data.name}.jpg"
            new_image_path = os.path.join(temp_dir, new_image_name)
            # Just to gaurantee that image is named after the user
            os.rename(original_image_path, new_image_path)

            user_folder = os.path.join(self.users_dir, user_data.user_id)
            os.makedirs(user_folder, exist_ok=True)
            
            final_image_path = os.path.join(user_folder, new_image_name)
            os.rename(new_image_path, final_image_path)
                        
            # Deleting the temporary image
            if os.path.exists(new_image_path):
                os.remove(new_image_path)
            
            return user_data.user_id
        else:
            raise FileNotFoundError(f"No image found in folder: {temp_dir}")


    def create_user(self, name, last_name, gender, user_id=None):
        """
        Add a user to Firebase and local with their image converted to Base64.
        -> There has to be an image of the user being made in the temp_user folder!!!

        Args:
            user_id (str): The user ID.
            name (str): The user's name.
            last_name (str): The user's last name.
            gender (str):
            user_id (str, optional): The user ID.
        
        Returns:
            str: The user ID.
        """
                    
        if not user_id:
            user_id = str(random.randint(100000, 999999))
        
        # Createing json file with user data
        user_data = {
            'name': name,
            'last_name': last_name,
            'user_id': user_id,
            'gender': gender
        }

        # Create locally
        self.add_user_local(user_data)

        # Direct to users folder
        user_folder = os.path.join(self.users_dir, user_id)
        if not os.path.exists(user_folder):
            raise FileNotFoundError(f"Folder for user_id {user_id} does not exist: {user_folder}")
        
        # Find image and data for user and send to database
        image_filename = self._find_first_image(user_folder)
        if image_filename:
            image_path = os.path.join(user_folder, image_filename)
            base64_image = image_to_base64(image_path)
            add_user(user_id, name, base64_image)
            return user_id
        else:
            raise FileNotFoundError(f"No image found in folder: {user_folder}")

    def get_user_image(self, user_id):
        """
        Retrieve a user's image from Firebase and save it to the faces folder.
        
        Args:
            user_id (str): The user ID.
        
        Returns:
            dict: User data including name and image path.
        """
        user_data = get_user(user_id)
        if user_data:
            image_name = f"{user_id}.jpg"
            base64_to_image(user_data['image_64'], user_id)
            return {
                'name': user_data['name'],
                'image_path': os.path.join(self.users_dir, image_name)
            }
        return None

    def update_user_image(self, user_id, name=None, image_path=None):
        """
        Update a user's information and/or image in Firebase.
        
        Args:
            user_id (str): The user ID.
            name (str, optional): The user's new name.
            image_path (str, optional): Path to the user's new image file.
        """
        base64_image = None
        if image_path:
            image_path = os.path.join(self.users_dir, image_path)
            base64_image = image_to_base64(image_path)
        update_user(user_id, name, base64_image)

    def delete_user_with_image(self, user_id):
        """
        Delete a user from Firebase and remove their image from the faces folder.
        
        Args:
            user_id (str): The user ID.
        """
        delete_user(user_id)
        image_path = os.path.join(self.users_dir, f"{user_id}.png")
        if os.path.exists(image_path):
            os.remove(image_path)

    def check_all_faces_in_folder(self):
        """
        Check whether all faces stored in Firebase are present in the faces folder.
        
        Returns:
            list: List of user IDs whose images are missing in the faces folder.
        """
        missing_images = []
        users = get_all_users()
        
        for user_id, user_data in users.items():
            image_path = os.path.join(self.users_dir, f"{user_id}.png")
            if not os.path.exists(image_path):
                missing_images.append(user_id)
        
        return missing_images
    
    def _find_first_image(self, folder_path):
        """
        Find the first image file in the given folder.
        
        Args:
            folder_path (str): Path to the folder.
        
        Returns:
            str: The filename of the first image found, or None if no image is found.
        """
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                return filename
        return None