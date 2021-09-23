from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mailman import Mail
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from src.chat.config import config_by_name

db = SQLAlchemy()
migrate = Migrate()
flask_bcrypt = Bcrypt()
cors = CORS()
mail = Mail()
redis = FlaskRedis()
sio = SocketIO()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    from src.chat.controller import api_bp
    app.register_blueprint(api_bp)

    db.init_app(app)
    migrate.init_app(app, db)
    flask_bcrypt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    redis.init_app(app)
    sio.init_app(app, cors_allowed_origins="*",
                 async_mode=app.config['ASYNC_MODE'],
                 message_queue=app.config['REDIS_URL'],
                 always_connect=True,
                 )

    return app
