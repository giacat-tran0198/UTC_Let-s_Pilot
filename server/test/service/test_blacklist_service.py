import unittest

from werkzeug.exceptions import InternalServerError

from src.chat import db
from src.chat.model.user import User
from src.chat.service.auth_service import encode_auth_token
from src.chat.service.blacklist_service import save_token_into_blacklist, check_blacklist
from test.base import BaseTestCase


class TestBlackListService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.seed()

    def seed(self):
        self.user = User(
            email='test@test.com',
            password='test',
            username='test user name',
            first_name='first name',
            last_name='last name',
        )
        db.session.add(self.user)
        db.session.commit()

    def test_save_black_token(self):
        auth_token, _ = encode_auth_token(self.user.id)
        try:
            save_token_into_blacklist(auth_token)
        except InternalServerError:
            self.fail('The server was unable to save your data')

    def test_check_token_in_black_list(self):
        auth_token, _ = encode_auth_token(self.user.id)
        save_token_into_blacklist(auth_token)
        self.assertTrue(check_blacklist(auth_token))


if __name__ == '__main__':
    unittest.main()
