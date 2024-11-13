from sqlite3 import OperationalError
from unittest.mock import patch
from flask import json
from core.services import UserService
from app import create_app
from extensions import db
from unittest import TestCase
from faker import Faker

class TestUserService(TestCase):
    
    @classmethod
    def setUpClass(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user_service = UserService()
        self.faker = Faker()
        self.client = self.app.test_client()  
        
    @classmethod
    def tearDownClass(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        passwd=self.faker.password()
        user_data = {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": passwd,
            "password2":passwd
        }
        new_user = self.user_service.create_user(user_data)
        self.assertIsNotNone(new_user.id)


    def test_signup_success(self):
        passwd=self.faker.password()
        new_user_data = {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": passwd,
            "password2":passwd
        }

        response = self.client.post('/api/auth/signup', data=json.dumps(new_user_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_login_success(self):
        passwd=self.faker.password()
        new_user_data = {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": passwd,
            "password2": passwd
        }
        self.client.post('/api/auth/signup', data=json.dumps(new_user_data), content_type='application/json')

        login_data = {
            "username": new_user_data["username"],
            "password": new_user_data["password"],
             "email": new_user_data["email"]
        }
        response = self.client.post('/api/auth/login', data=json.dumps(login_data), content_type='application/json')
        self.assertEqual(response.status_code, 200) 
    
    def test_login_invalid_credentials(self):
        login_data = {
            "username": "invalid_username",
            "password": "invalid_password",
            "email": "invalid_email",
        }
        response = self.client.post('/api/auth/login', data=json.dumps(login_data), content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_signup_db_error(self):
        passwd=self.faker.password()
        new_user_data = {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": passwd,
            "password2":passwd
        }

        with patch('adapters.api.controllers.UserService.create_user', side_effect=OperationalError("DB error", None, None)):
            response = self.client.post('/api/auth/signup', data=json.dumps(new_user_data), content_type='application/json')
            self.assertEqual(response.status_code, 500)
            self.assertIn('There was an issue accessing the database', response.json['error']['message'])

    def test_login_db_error(self):
        login_data = {
            "username": self.faker.user_name(),
            "password": self.faker.password(),
             "email": self.faker.email(),
        }

        with patch('adapters.api.controllers.UserService.login', side_effect=OperationalError("DB error", None, None)):
            response = self.client.post('/api/auth/login', data=json.dumps(login_data), content_type='application/json')
            self.assertEqual(response.status_code, 500)
            self.assertIn('There was an issue accessing the database', response.json['error']['message'])

