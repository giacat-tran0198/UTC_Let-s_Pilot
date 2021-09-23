"""Class definition for PushSubscription."""

from src.chat import db


class PushSubscription(db.Model):
    """Token Model for storing JWT tokens."""
    __tablename__ = 'push_subscription'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    subscription_json = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
        return '<user_id: {} subscription: {}>'.format(self.user_id, self.subscription_json)
