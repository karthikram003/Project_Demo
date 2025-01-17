import time
import unittest
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from tests.utils.common_functions import get_token, set_up_class, tear_down_class
from app.utils.config_loader import config
from main import app
 
client = TestClient(app)
 
class TestUserController(unittest.TestCase):
 
 
    @classmethod
    def setUpClass(cls):
        set_up_class(cls)
 
    @classmethod
    def tearDownClass(cls):
        tear_down_class(cls)
 
    @staticmethod
    def auth_header():
        return {"Authorization": f"Bearer {get_token()}"}
 
    @patch("app.services.user_service.get_user_by_email")
    def test_user_controller_login_successful_if_user_already_exists(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = True
        response = client.post("/api/v1/users/login", headers=self.auth_header())
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json(), {"message": "User successfully logged in"})
 
    @patch("app.services.user_service.create_user")
    @patch("app.services.user_service.get_user_by_email")
    def test_user_controller_login_successful_if_user_not_exists(self, mock_get_user_by_email, mock_create_user):
        mock_create_user.return_value = True
        mock_get_user_by_email.return_value = False
        response = client.post("/api/v1/users/login", headers=self.auth_header())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "User successfully logged in"})
 
    def test_user_controller_login_when_token_has_expired(self):
        self.mock_validate_token.return_value = {
            "iss": config['JWT_ISSUER'],
            "exp": time.time() - 100
        }
        response = client.post("/api/v1/users/login/", headers=self.auth_header())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Token has expired"})
 
    def test_user_controller_login_when_invalid_token_issuer(self):
        self.mock_validate_token.return_value = {
            "iss": None,
            "exp": time.time()
        }
        response = client.post("/api/v1/users/login/", headers=self.auth_header())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Invalid token issuer'})
 
 
    def test_user_controller_login_when_token_is_invalid(self):
        self.mock_validate_token.return_value = None
        response = client.post("/api/v1/users/login/", headers={"Authorization": "Bearer: test"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Missing or invalid authorization header"})
 
    def test_user_controller_login_when_token_is_missing(self):
        self.mock_validate_token.return_value = None
        response = client.post("/api/v1/users/login/", headers={"Authorization": "Bearer"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Missing or invalid authorization header"})
 
    def test_user_controller_login_when_header_is_empty(self):
        self.mock_validate_token.return_value = None
        response = client.post("/api/v1/users/login/", headers={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Missing or invalid authorization header"})
 
    def test_user_controller_login_when_header_is_none(self):
        self.mock_validate_token.return_value = None
        response = client.post("/api/v1/users/login/", headers=None)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Missing or invalid authorization header"})
 
    def test_user_controller_login_when_header_is_missing(self):
        self.mock_validate_token.return_value = None
        response = client.post("/api/v1/users/login/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Missing or invalid authorization header"})
 
    def test_user_controller_login_when_internal_server_error(self):
        self.mock_validate_token.return_value = {
            "iss": config['JWT_ISSUER'],
            "exp": time.time() + 100
        }
        response = client.post("/api/v1/users/login", headers=self.auth_header())
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Internal server error'})