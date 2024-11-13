from sqlite3 import OperationalError
import unittest
from unittest.mock import patch
from flask_restful import Api
from faker import Faker
from app import create_app
from adapters.api.controllers import VideoController

class VideoControllerTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True 
        self.client = self.app.test_client()  
        self.fake = Faker()  
        self.api = Api(self.app)
        self.api.add_resource(VideoController, '/api/videos', '/api/videos/<string:filename>')

    @patch('adapters.api.controllers.send_from_directory')
    def test_get_file_video_success(self, mock_send_from_directory):
        mock_send_from_directory.return_value = 'file content'

        response = self.client.get('/api/videos/testfile.mp4')
        self.assertEqual(response.status_code, 200)

    @patch('adapters.api.controllers.send_from_directory')
    def test_get_file_video_database_error(self, mock_send_from_directory):
        mock_send_from_directory.side_effect = OperationalError('database is locked')

        response = self.client.get('/api/videos/testfile.mp4')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json)
        self.assertIn('There was an issue accessing the database.', response.json['error']['message'])

    @patch('adapters.api.controllers.send_from_directory')
    def test_get_file_video_unexpected_error(self, mock_send_from_directory):
        mock_send_from_directory.side_effect = Exception('unexpected error')

        response = self.client.get('/api/videos/testfile.mp4')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json)
        self.assertIn('An unexpected error occurred.', response.json['error']['message'])

    @patch('adapters.api.controllers.VideoService')
    def test_get_all_videos_success(self, mock_video_service):
        mock_video_service.return_value.get_all_videos.return_value = []

        response = self.client.get('/api/videos')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    @patch('adapters.api.controllers.VideoService')
    def test_get_all_videos_database_error(self, mock_video_service):
        mock_video_service.return_value.get_all_videos.side_effect = OperationalError('database is locked')

        response = self.client.get('/api/videos')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json)
        self.assertIn('There was an issue accessing the database.', response.json['error']['message'])

    @patch('adapters.api.controllers.VideoService')
    def test_get_all_videos_unexpected_error(self, mock_video_service):
        mock_video_service.return_value.get_all_videos.side_effect = Exception('unexpected error')

        response = self.client.get('/api/videos')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json)
        self.assertIn('An unexpected error occurred.', response.json['error']['message'])

if __name__ == '__main__':
    unittest.main()