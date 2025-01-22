import os
import json
import unittest
from unittest.mock import patch, MagicMock
from src.facial_imagery.user_image_manager import add_user_with_image, get_user_image, update_user_image, delete_user_with_image, check_all_faces_in_folder

class TestUserImageManager(unittest.TestCase):

    @patch('src.firebase.fire.add_user')
    @patch('src.facial_imagery.image_conversions.image_to_base64')
    def test_add_user_with_image(self, mock_image_to_base64, mock_add_user):
        mock_image_to_base64.return_value = "base64_string"
        user_id = add_user_with_image("Test User", "spaceship2.jpg")
        mock_add_user.assert_called_once_with(user_id, "Test User", "base64_string")

    @patch('src.firebase.fire.get_user')
    @patch('src.facial_imagery.image_conversions.base64_to_image')
    def test_get_user_image(self, mock_base64_to_image, mock_get_user):
        mock_get_user.return_value = {
            'name': 'Test User',
            'image_64': 'base64_string'
        }
        user_data = get_user_image("test_user_id")
        mock_base64_to_image.assert_called_once_with('base64_string', 'test_user_id.png')
        self.assertEqual(user_data['name'], 'Test User')
        self.assertTrue(os.path.exists(user_data['image_path']))

    @patch('src.firebase.fire.update_user')
    @patch('src.facial_imagery.image_conversions.image_to_base64')
    def test_update_user_image(self, mock_image_to_base64, mock_update_user):
        mock_image_to_base64.return_value = "new_base64_string"
        update_user_image("test_user_id", name="Updated User", image_path="spaceship2.jpg")
        mock_update_user.assert_called_once_with("test_user_id", "Updated User", "new_base64_string")

    @patch('src.firebase.fire.delete_user')
    def test_delete_user_with_image(self, mock_delete_user):
        delete_user_with_image("test_user_id")
        mock_delete_user.assert_called_once_with("test_user_id")
        self.assertFalse(os.path.exists(os.path.join('faces', 'test_user_id.png')))

    @patch('src.firebase.fire.get_all_users')
    @patch('src.facial_imagery.image_conversions.base64_to_image')
    def test_check_all_faces_in_folder(self, mock_base64_to_image, mock_get_all_users):
        mock_get_all_users.return_value = {
            'user1': {'name': 'User One', 'image_64': 'base64_string1'},
            'user2': {'name': 'User Two', 'image_64': 'base64_string2'}
        }
        missing_images = check_all_faces_in_folder()
        mock_base64_to_image.assert_any_call('base64_string1', 'user1.png')
        mock_base64_to_image.assert_any_call('base64_string2', 'user2.png')
        self.assertEqual(missing_images, [])

if __name__ == '__main__':
    unittest.main()