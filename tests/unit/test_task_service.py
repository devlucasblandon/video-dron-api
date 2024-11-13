import os
from sqlite3 import OperationalError
import unittest
from unittest.mock import patch
from flask_restful import Api
from faker import Faker
from app import create_app
from adapters.api.controllers import TaskController

class TaskControllerTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True 
        self.client = self.app.test_client()  
        self.fake = Faker()  
        self.api = Api(self.app)
        self.api.add_resource(TaskController, '/api/tasks', '/api/tasks/<int:id_task>')

    @patch('adapters.api.controllers.TaskService')
    def test_get_tasks_success(self, mock_task_service):
        mock_task_service.return_value.get_all.return_value = []
        response = self.client.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    @patch('adapters.api.controllers.TaskService')
    def test_get_task_by_id_success(self, mock_task_service):
        task_data = {'task': {'id': 1, 'name': 'Test Task'}, 'video_url': 'http://example.com/video.mp4'}
        mock_task_service.return_value.get_task_by_id.return_value = task_data

        response = self.client.get('/api/tasks/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['task']['id'], 1)
        self.assertEqual(response.json['video_url'], 'http://example.com/video.mp4')

    @patch('adapters.api.controllers.TaskService')
    def test_get_task_by_id_not_found(self, mock_task_service):
        mock_task_service.return_value.get_task_by_id.return_value = None

        response = self.client.get('/api/tasks/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['msg'], 'Task not found')

    def test_create_task_no_file(self):
        response = self.client.post('/api/tasks', data={}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'No selected file')

    @patch('adapters.api.controllers.TaskService')
    def test_delete_task_success(self, mock_task_service):
        mock_task_service.return_value.delete_task.return_value = True

        response = self.client.delete('/api/tasks/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Task deleted successfully')

    @patch('adapters.api.controllers.TaskService')
    def test_get_tasks_database_error(self, mock_task_service):
        mock_task_service.return_value.get_all_tasks.side_effect = OperationalError('DB error')

        response = self.client.get('/api/tasks')
        self.assertEqual(response.status_code, 500)
        self.assertIn('There was an issue accessing the database', response.json['error']['message'])

if __name__ == '__main__':
    unittest.main()