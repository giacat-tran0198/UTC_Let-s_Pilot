"""Config settings for for development, testing and production environments."""

from os import path, getenv

# uncomment the line below for postgres database url from environment variable
postgres_local_base = getenv('SQLALCHEMY_DATABASE_URI', '')

basedir = path.abspath(path.dirname(__file__))


class Config:
    APPLICATION = getenv('APPLICATION')

    SECRET_KEY = getenv('SECRET_KEY', 'my_secret_key')
    DEBUG = False
    RESTX_ERROR_404_HELP = False
    RESTX_MASK_SWAGGER = False
    TOKEN_EXPIRE_HOURS = int(getenv('TOKEN_EXPIRE_HOURS', '0'))
    TOKEN_EXPIRE_MINUTES = int(getenv('TOKEN_EXPIRE_MINUTES', '0'))

    # Flask Mail
    MAIL_SERVER = getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(getenv('MAIL_PORT', 25))
    MAIL_USE_TLS = getenv('MAIL_USE_TLS', 'false').lower() in ('true', '1', 't')
    MAIL_USE_SSL = getenv('MAIL_USE_SSL', 'false').lower() in ('true', '1', 't')
    MAIL_USERNAME = getenv('MAIL_USERNAME', None)
    MAIL_PASSWORD = getenv('MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = getenv('MAIL_DEFAULT_SENDER', 'Chat Server')

    # Redis
    REDIS_URL = getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Socketio
    ASYNC_MODE = getenv('ASYNC_MODE')

    # File upload
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc'}

    # Vapid
    VAPID_PRIVATE_KEY = getenv('VAPID_PRIVATE_KEY')
    VAPID_PUBLIC_KEY = getenv('VAPID_PUBLIC_KEY')
    VAPID_CLAIMS = dict(
        sub='mailto:' + getenv('VAPID_CLAIMS_SUB', 'test@test.com')
    )

    # SSL
    SSL_PRIVATE_KEY = path.join(basedir, '../..', 'https', 'tx_chat.key')
    SSL_CERTIFICATE_KEY = path.join(basedir, '../..', 'https', 'tx_chat-certificate.crt')


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base if postgres_local_base else \
        'sqlite:///' + path.join(basedir, '../../flask_chat_main.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_EXPIRE_MINUTES = int(getenv('TOKEN_EXPIRE_MINUTES', '15'))


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, '../../flask_chat_test.db')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    SQLALCHEMY_DATABASE_URI = postgres_local_base
    TOKEN_EXPIRE_HOURS = 24


config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
    test=TestingConfig,
)
