"""Class definition for BlacklistedToken."""

from src.chat import db


class BlacklistedToken(db.Model):
    """Token Model for storing JWT tokens."""
    __tablename__ = 'blacklisted_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return '<token: {}'.format(self.token)
