import os
import shutil
import random
import json
import hashlib
import time
from .fire import FirebaseManager
from .image_conversions import ImageConversions

class UserImageManager:
    def __init__(self):
        self.users_dir = os.path.join(os.path.dirname(__file__), '..', 'local_database', 'users')
        self.temp_dir = os.path.abspath(os.path.join(self.users_dir, '..', 'temp_user'))
        self.firebase_manager = FirebaseManager()

    def generate_numeric_id(self):
        unique_str = str(time.time()).encode()  # Usa timestamp para garantir unicidade
        hash_value = hashlib.sha1(unique_str).hexdigest()  # Gera um hash hexadecimal
        numeric_id = int(hash_value, 16)  # Converte o hash hexadecimal para um número inteiro
        return str(numeric_id)[:10]  # Retorna apenas os primeiros 10 dígitos

    def add_user_local(self, user_data, user_id):
        """
            Add a user to Firebase with their image stored locally.
            Used when a new user is being made
            -> There has to be an image of the user being made in the temp_user folder!!!
            -> Meant to be used by other functions
        
        Args:
            name (str): The user's name.
            user_data (dict): The user's data.
            user_id (str, optional): The user ID.
        
        Returns:
            str: Message indicating that the user was created successfully.
        """
        
        image_filename = self._find_first_image(self.temp_dir)
        
        if image_filename:
            original_image_path = os.path.join(self.temp_dir, image_filename)
            new_image_name = f"{user_data['name']}.jpg"
            new_image_path = os.path.join(self.temp_dir, new_image_name)
            # Just to guarantee that image is named after the user
            os.rename(original_image_path, new_image_path)

            user_folder = os.path.join(self.users_dir, user_id)
            os.makedirs(user_folder, exist_ok=True)
            
            final_image_path = os.path.join(user_folder, new_image_name)
            os.rename(new_image_path, final_image_path)

            # Save user data as JSON in the same folder
            user_data_path = os.path.join(user_folder, f"{user_data['user_id']}.json")
            with open(user_data_path, 'w') as json_file:
                json.dump(user_data, json_file, indent=4)
            
            return user_id
        else:
            raise FileNotFoundError(f"No image found in folder: {self.temp_dir}")
        
    
    def get_all_users(self):
        """
        Get all users from Firebase.
        
        Returns:
            dict: Dictionary containing all user data.
        """
        return self.firebase_manager.get_all_users()


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
            str: Message indicating that the user was created successfully.
            -> Output of file is at users folder
        """
        
        # Creating 6 digit id
        #if not user_id:
        #    user_id = str(random.randint(100000, 999999))
        if not user_id:
            user_id = self.generate_numeric_id()

        # Createing json file with user data
        user_data = {
            'name': name,
            'last_name': last_name,
            'user_id': user_id,
            'gender': gender
        }

        # Create locally
        self.add_user_local(user_data, user_id)

        # Direct to users folder
        user_folder = os.path.join(self.users_dir, user_id)
        if not os.path.exists(user_folder):
            raise FileNotFoundError(f"Error looking for {user_id}'s folder")
        
        # Find image and data for user and send to database
        image_filename = self._find_first_image(user_folder)

        # Adds user to firebase
        if image_filename:
            image_path = os.path.join(user_folder, image_filename)
            base64_image = ImageConversions.image_to_base64(image_path)
            user_data['image_64'] = base64_image
            self.firebase_manager.add_user(user_id, user_data)
            return user_id
        else:
            raise FileNotFoundError(f"No image found in temporary folder: {user_folder}")

    def update_user_data(self, name, last_name, gender, user_id):
        """
        Update a user's information and/or image in Firebase.
        -> Needs an image in the temp_user folder!!!

        Args:
            user_id (str): The user ID.
            name (str, optional): The user's new name.
            last_name (str, optional): The user's new last name.
            gender (str, optional): The user's new

        Returns:
            str: Message indicating that the user was updated successfully.
        """

        user_data = {
            'name': name,
            'last_name': last_name,
            'gender': gender,
            'user_id': user_id,
        }
        print(f" Antes do try:Atualizando usuário {user_id} com os dados: {user_data}")

        try:
            print(f"Depois do try: Atualizando usuário {user_id} com os dados: {user_data}")
            # Create locally
            self.add_user_local(user_data, user_id)

            # Direct to users folder
            user_folder = os.path.join(self.users_dir, user_id)
            if not os.path.exists(user_folder):
                raise FileNotFoundError(f"Error looking for {user_id}'s folder")
            
            # Find image and data for user and send to database
            image_filename = self._find_first_image(user_folder)

            # Adds user to firebase
            if image_filename:
                image_path = os.path.join(user_folder, image_filename)
                base64_image = ImageConversions.image_to_base64(image_path)
                user_data['image_64'] = base64_image
                self.firebase_manager.update_user(user_id, user_data)
                return user_id
            else:
                raise FileNotFoundError(f"No image found in temporary folder: {user_folder}")
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise


    def delete_user(self, user_id):
        """
        Delete a user from Firebase and local storage.

        Args:
            user_id (str): The user ID.
        
        Returns:
            str: Message indicating that the user was deleted successfully.
        """
        # Delete user from Firebase
        self.firebase_manager.delete_user(user_id)

        # Delete user from local storage
        user_folder = os.path.join(self.users_dir, user_id)
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
            return f"User {user_id} deleted successfully."
        else:
            raise FileNotFoundError(f"User folder not found: {user_folder}")

    def recover_users(self):
        """
        Check whether all faces stored in Firebase are present in the faces folder.
        
        Returns:
            list: List of user IDs whose images are missing in the faces folder.
        """
        # Delete the existing users folder
        if os.path.exists(self.users_dir):
            shutil.rmtree(self.users_dir)
        
        # Create a new users folder
        os.makedirs(self.users_dir, exist_ok=True)

        # Getting users from Firebase
        users = self.firebase_manager.get_all_users()
        user_ids = []

        # Iterating users to add locally
        for user_id, user_data in users.items():
            user_folder = os.path.join(self.users_dir, user_id)
            os.makedirs(user_folder, exist_ok=True)
            
            # Save user data as JSON in the same folder
            user_data_path = os.path.join(user_folder, f"{user_id}.json")
            with open(user_data_path, 'w') as json_file:
                json.dump(user_data, json_file, indent=4)
            
            # Save the user's image in the same folder
            image_path = os.path.join(user_folder, f"{user_data['name']}.jpg")
            image_data = ImageConversions.base64_to_image(user_data['image_64'], image_path)
            with open(image_path, "wb") as output_file:
                output_file.write(image_data)
            user_ids.append(user_id)
        
        return "Successfully recovered the following ids: " + str(user_ids)
    
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