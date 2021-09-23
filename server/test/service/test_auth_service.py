import time
import unittest

from werkzeug.exceptions import Unauthorized

from src.chat import db
from src.chat.model.user import User
from src.chat.service.auth_service import (encode_auth_token, decode_auth_token, login_user, logout_user, refresh_token,
                                           decode_auth_admin_token)
from src.chat.service.blacklist_service import save_token_into_blacklist
from test.base import BaseTestCase


class TestAuthService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.seed()

    def seed(self):
        self.user = User(
            email='test@test.com',
            password='test',
            username='username',
            first_name='first name',
            last_name='last name',
        )
        db.session.add(self.user)
        db.session.commit()

    def test_encode_auth_token(self):
        auth_token, expire_in = encode_auth_token(self.user.id)

        self.assertIsInstance(auth_token, str)
        self.assertEqual(5, expire_in)

    def test_decode_auth_token_success(self):
        auth_token, expire_in = encode_auth_token(self.user.id)
        user_id, admin = decode_auth_token(auth_token)
        self.assertIsInstance(auth_token, str)
        self.assertEqual(5, expire_in)
        self.assertEqual(1, user_id)
        self.assertFalse(admin)

    def test_decode_auth_admin_token_success(self):
        auth_token, expire_in = encode_auth_token(self.user.id, True)
        user_id, admin = decode_auth_token(auth_token)
        self.assertIsInstance(auth_token, str)
        self.assertEqual(5, expire_in)
        self.assertEqual(1, user_id)
        self.assertTrue(admin)

        # decode auth admin token
        auth_token, expire_in = encode_auth_token(self.user.id, True)
        user_id = decode_auth_admin_token(auth_token)
        self.assertIsInstance(auth_token, str)
        self.assertEqual(5, expire_in)
        self.assertEqual(1, user_id)

    def test_decode_auth_token_in_blacklist(self):
        auth_token, expire_in = encode_auth_token(self.user.id)
        save_token_into_blacklist(auth_token)

        self.assertIsInstance(auth_token, str)
        self.assertEqual(5, expire_in)

        with self.assertRaises(Unauthorized) as unauth:
            decode_auth_token(auth_token)
            self.assertIn('Token was removed.', str(unauth.exception))

    def test_decode_auth_admin_token_not_admin(self):
        auth_token, expire_in = encode_auth_token(self.user.id)

        with self.assertRaises(Unauthorized) as unauth:
            decode_auth_admin_token(auth_token)
            self.assertIn('You are not an administrator.', str(unauth.exception))

    @unittest.skip("So slower for test sleep")
    def test_decode_auth_token_expired(self):
        auth_token, expire_in = encode_auth_token(self.user.id)
        self.assertIsInstance(auth_token, str)
        self.assertEqual(5, expire_in)
        time.sleep(6)
        with self.assertRaises(Unauthorized) as unauth:
            decode_auth_token(auth_token)
            self.assertIn('Signature expired.', str(unauth.exception))

    def test_decode_auth_invalid_token(self):
        auth_token, expire_in = encode_auth_token(self.user.id)
        self.assertIsInstance(auth_token, str)
        self.assertEqual(5, expire_in)
        with self.assertRaises(Unauthorized) as unauth:
            decode_auth_token(auth_token + '123')
            self.assertIn('Invalid token.', str(unauth.exception))

    def test_login_success(self):
        response = login_user(email='test@test.com', password='test')
        self.assertIsNotNone(response['authorization'])
        self.assertIsNotNone(response['token_expires_in'])
        self.assertEqual(5, response['token_expires_in'])
        self.assertIsNotNone(response['token_type'])
        self.assertEqual('Bearer', response['token_type'])

    def test_login_error_fault_email(self):
        with self.assertRaises(Unauthorized) as unauth:
            login_user(email='test1@test.com', password='test')
            self.assertEqual('Email or Password does not match.', str(unauth.exception))

    def test_login_error_fault_password(self):
        with self.assertRaises(Unauthorized) as unauth:
            login_user(email='test@test.com', password='test1')
            self.assertEqual('Email or Password does not match.', str(unauth.exception))

    def test_logout_success(self):
        auth_token, _ = encode_auth_token(self.user.id)
        response = logout_user(auth_token)
        self.assertIsNotNone(response['message'])

    def test_refresh_token(self):
        response = refresh_token(self.user.id)
        self.assertIsNotNone(response['authorization'])
        self.assertIsNotNone(response['token_expires_in'])
        self.assertEqual(5, response['token_expires_in'])
        self.assertIsNotNone(response['token_type'])
        self.assertEqual('Bearer', response['token_type'])


if __name__ == '__main__':
    unittest.main()
