import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from src.facial_imagery.user_image_manager import UserImageManager
from src.facial_imagery.image_conversions import image_to_base64, base64_to_image

class TestUserImageManager(unittest.TestCase):

    def setUp(self):
        self.manager = UserImageManager()

    @patch('src.firebase.fire.add_user')
    @patch('src.facial_imagery.image_conversions.image_to_base64')
    def test_add_user_with_image(self, mock_image_to_base64, mock_add_user):
        mock_image_to_base64.return_value = "base64_string"
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faces", "spaceship2.jpg")
        user_id = self.manager.add_user_with_image("Test User", image_path)
        mock_add_user.assert_called_once_with(user_id, "Test User", "base64_string")

    @patch('src.firebase.fire.get_user')
    @patch('src.facial_imagery.image_conversions.base64_to_image')
    def test_get_user_image(self, mock_base64_to_image, mock_get_user):
        mock_get_user.return_value = {
            'name': 'Test User',
            'image_64': 'base64_string'
        }
        user_data = self.manager.get_user_image("test_user_id")
        mock_base64_to_image.assert_called_once_with('base64_string', os.path.join(self.manager.faces_dir, 'test_user_id.png'))
        self.assertEqual(user_data['name'], 'Test User')
        self.assertTrue(os.path.exists(user_data['image_path']))

    @patch('src.firebase.fire.update_user')
    @patch('src.facial_imagery.image_conversions.image_to_base64')
    def test_update_user_image(self, mock_image_to_base64, mock_update_user):
        mock_image_to_base64.return_value = "new_base64_string"
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faces", "spaceship2.jpg")
        self.manager.update_user_with_image("test_user_id", name="Updated User", image_path=image_path)
        mock_update_user.assert_called_once_with("test_user_id", "Updated User", "new_base64_string")

    @patch('src.firebase.fire.delete_user')
    def test_delete_user_with_image(self, mock_delete_user):
        self.manager.delete_user_with_image("test_user_id")
        mock_delete_user.assert_called_once_with("test_user_id")
        self.assertFalse(os.path.exists(os.path.join(self.manager.faces_dir, 'test_user_id.png')))

    @patch('src.firebase.fire.get_all_users')
    def test_check_all_faces_in_folder(self, mock_get_all_users):
        mock_get_all_users.return_value = {
            'user1': {'name': 'User One', 'image_64': 'base64_string'},
            'user2': {'name': 'User Two', 'image_64': 'base64_string'}
        }
        missing_images = self.manager.check_all_faces_in_folder()
        self.assertIsInstance(missing_images, list)

if __name__ == '__main__':
    unittest.main()