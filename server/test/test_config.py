import unittest

from flask import current_app
from flask_testing import TestCase

from app import app


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('src.chat.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertIsNot(app.config['SECRET_KEY'], 'my_precious')
        self.assertTrue(app.config['DEBUG'])
        self.assertIsNotNone(current_app)
        self.assertIn('flask_chat_main.db', app.config['SQLALCHEMY_DATABASE_URI'])
        self.assertGreaterEqual(app.config['TOKEN_EXPIRE_HOURS'], 0)
        self.assertGreaterEqual(app.config['TOKEN_EXPIRE_MINUTES'], 0)
        self.assertIsNotNone(app.config['MAIL_USERNAME'])
        self.assertIsNotNone(app.config['MAIL_PASSWORD'])
        self.assertIsNotNone(app.config['MAIL_DEFAULT_SENDER'])


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('src.chat.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertIsNot(app.config['SECRET_KEY'], 'my_precious')
        self.assertTrue(app.config['DEBUG'])
        self.assertIn('flask_chat_test.db', app.config['SQLALCHEMY_DATABASE_URI'])
        self.assertIsNotNone(app.config['MAIL_USERNAME'])
        self.assertIsNotNone(app.config['MAIL_PASSWORD'])
        self.assertIsNotNone(app.config['MAIL_DEFAULT_SENDER'])


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('src.chat.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertFalse(app.config['DEBUG'])
        self.assertNotIn('flask_chat_main.db', app.config['SQLALCHEMY_DATABASE_URI'])
        self.assertNotIn('flask_chat_test.db', app.config['SQLALCHEMY_DATABASE_URI'])
        self.assertGreaterEqual(app.config['TOKEN_EXPIRE_HOURS'], 0)
        self.assertGreaterEqual(app.config['TOKEN_EXPIRE_MINUTES'], 0)
        self.assertIsNotNone(app.config['MAIL_USERNAME'])
        self.assertIsNotNone(app.config['MAIL_PASSWORD'])
        self.assertIsNotNone(app.config['MAIL_DEFAULT_SENDER'])


if __name__ == '__main__':
    unittest.main()
