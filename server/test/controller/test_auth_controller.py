import json
import unittest

from flask import url_for

from src.chat import db
from src.chat.model.user import User
from test.base import BaseTestCase


def login_user(client, email='test@test.com', password='test'):
    return client.post(
        url_for('api.auth_login'),
        data=json.dumps(dict(
            email=email,
            password=password
        )),
        content_type='application/json'
    )


class TestAuthController(BaseTestCase):

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

    def test_user_login_success(self):
        with self.client as client:
            login_response = login_user(client)
            response = json.loads(login_response.data)

            self.assert200(login_response)

            self.assertIsNotNone(response['authorization'])
            self.assertIsNotNone(response['token_expires_in'])
            self.assertEqual(5, response['token_expires_in'])
            self.assertIsNotNone(response['token_type'])
            self.assertEqual('Bearer', response['token_type'])

    def test_user_login_require_email(self):
        with self.client as client:
            login_response = login_user(client, email=None)
            response = json.loads(login_response.data)

            self.assert400(login_response)
            self.assertIsNotNone(response['errors'])
            self.assertIsNotNone(response['errors']['email'])

    def test_user_login_require_email_correct_format_email(self):
        with self.client as client:
            login_response = login_user(client, email='test')
            response = json.loads(login_response.data)

            self.assert400(login_response)
            self.assertIsNotNone(response['errors'])
            self.assertIsNotNone(response['errors']['email'])

    def test_user_login_require_password(self):
        with self.client as client:
            login_response = login_user(client, password=None)
            response = json.loads(login_response.data)

            self.assert400(login_response)
            self.assertIsNotNone(response['errors'])
            self.assertIsNotNone(response['errors']['password'])

    def test_user_login_not_match_email(self):
        with self.client as client:
            login_response = login_user(client, email='123@test.com')
            response = json.loads(login_response.data)

            self.assert401(login_response)
            self.assertIsNotNone(response['message'])
            self.assertEqual('Email or Password does not match.', response['message'])

    def test_user_login_not_match_password(self):
        with self.client as client:
            login_response = login_user(client, password='123')
            response = json.loads(login_response.data)

            self.assert401(login_response)
            self.assertIsNotNone(response['message'])
            self.assertEqual('Email or Password does not match.', response['message'])

    def test_valid_logout_success(self):
        with self.client as client:
            login_response = login_user(client)
            response = json.loads(login_response.data)

            response = client.get(
                url_for('api.auth_logout'),
                headers=dict(Authorization=response['token_type'] + ' ' + response['authorization'])
            )
            data = json.loads(response.data)

            self.assert200(response)
            self.assertIsNotNone(data['message'])


if __name__ == '__main__':
    unittest.main()
