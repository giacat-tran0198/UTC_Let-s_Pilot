"""Service logic for user."""

import json
import random
import string
from http import HTTPStatus
from typing import Dict, Tuple

from flask import current_app
from flask_mailman import EmailMultiAlternatives
from werkzeug.exceptions import Conflict, InternalServerError, BadRequest

from src.chat import db, redis
from src.chat.model.pagination import Pagination
from src.chat.model.push_subscription import PushSubscription
from src.chat.model.user import User
from src.chat.service import save_data, delete_data
from src.chat.service.auth_service import generate_token
from src.chat.util.constant import TYPE_NOTIFICATION_ACTION_USER, TYPE_NOTIFICATION_ADMIN_USER, \
    TYPE_NOTIFICATION_ARCHIVE_USER
from src.chat.util.pagination import paginate
from src.chat.util.stream import sub_webpush, publish, sub_user_channel

STYLE_HTML = '''
<style type="text/css">
.email-container{
    font-family:arial;
    font-size:16px;
    margin:20px 20px 20px 20px;
}

h1{
    text-align:center;
    margin-bottom:30px;
}

p{
    text-align:center;
    margin-bottom:20px;
}

em{
    font-style: normal;
    font-weight:bold;
}
</style>
'''


def save_new_user(data: Dict[str, str]) -> Tuple[Dict[str, str], int]:
    """Create new user."""
    user = User.query.filter((User.email == data.get('email')) | (User.username == data.get('username'))).first()
    if not user:
        new_user = User(
            email=data.get('email'),
            username=data.get('username'),
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            ava=data.get('ava', None)
        )
        save_data(new_user)
        return generate_token(user_id=new_user.id, message='Successfully registered.'), HTTPStatus.CREATED
    raise Conflict('User already exists. Please Log in.')


def get_all_users(filter_by) -> Pagination:
    """
    Get all user for pagination.

    :param filter_by: The key want to filter
    :return pagination for user
    """
    query = User.query

    if filter_by:
        query = query.filter((User.username.like(f'%{filter_by}%'))
                             | (User.first_name.like(f'%{filter_by}%'))
                             | (User.last_name.like(f'%{filter_by}%'))
                             | (User.username.like(f'%{filter_by}%'))
                             )

    return paginate(query)


def get_a_user(id: int) -> User:
    """Find user by id."""
    return User.query.filter_by(id=id).first_or_404('User Not Found')


def update_a_user(id: int, new_data) -> Dict:
    """Update user's data."""

    user = get_a_user(id)

    try:
        for k, v in new_data.items():
            setattr(user, k, v)
        db.session.commit()
        return dict(message='Your profile was successfully changed')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to save your data.")


def update_a_user_password(id: int, data: Dict) -> Dict:
    """Update new password."""

    user = get_a_user(id)
    errors = dict()
    if not user.check_password(data.get('older_password')):
        errors['older_password'] = "'older_password' is not correct"
    if user.check_password(data.get('new_password')):
        errors['new_password'] = "'new_password' must be different from old"
    if len(errors) != 0:
        e = BadRequest()
        e.data = dict(
            errors=errors,
            message='Input payload validation failed'
        )
        raise e

    try:
        user.password = data.get('new_password')
        db.session.commit()
        return dict(message='Your password was successfully changed')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to save your data.")


def update_password_forgotten(email: str) -> Dict:
    """Reset the user's password when he forgot and send him an email."""

    user = User.query.filter_by(email=email).first_or_404(f'{email} is not exist.')

    letters = string.ascii_lowercase
    new_password = ''.join(random.choice(letters) for _ in range(8))

    try:
        user.password = new_password
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to save your data.")

    try:
        html_content = f'''
<div class="email-container">
    <h1>{current_app.config['APPLICATION']}</h1>
    <p>Hello <em>@{user.username}</em>, we received a request to reset your password.</p>
    <p>Your new password is : <em>{new_password}</em>.</p>
    <p>If you did not request to reset your password, please send an email to : <em>{current_app.config['MAIL_DEFAULT_SENDER']}</em>.</p>
</div>
{STYLE_HTML}
        '''

        msg = EmailMultiAlternatives(
            subject='Reset random password',
            body=f"{current_app.config['APPLICATION']}\n"
                 f"Hello @{user.username}, we received a request to reset your password.\n"
                 f"Your new password is: {new_password}\n"
                 f"If you did not request to reset your password, please send an email to : {current_app.config['MAIL_DEFAULT_SENDER']}.",
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to send your email.")

    return dict(message=f'Your new password was successfully sent your email {email}.')


def save_data_subscription_webpub(data: Dict, user_id: int) -> Dict:
    """Save the client's key when he subscribe webpub."""

    push_subscription = PushSubscription.query.filter_by(user_id=user_id).first()
    if not push_subscription:
        push_subscription = PushSubscription(
            user_id=user_id,
            subscription_json=json.dumps(data)
        )
        save_data(push_subscription)
    else:
        try:
            push_subscription.subscription_json = json.dumps(data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(str(e), exc_info=True)
            raise InternalServerError("The server encountered an internal error and was unable to save your data.")

    channel = sub_webpush(sub_user_channel(push_subscription.user_id))
    redis.set(channel, push_subscription.subscription_json)

    return dict(message="Stored the client's key.")


def unsubscription_data_subscription_webpub(user_id: int) -> Dict:
    """Delete the subscription webpub stored."""

    push_subscription = PushSubscription.query.filter_by(user_id=user_id) \
        .first_or_404('Service Worker Key was not found.')
    delete_data(push_subscription)

    channel = sub_webpush(sub_user_channel(user_id))
    redis.delete(channel)

    return dict(message="Unsubscribed the client's key.")


def transfer_subscription_to_redis() -> None:
    """Transfer data subscription from db to redis."""

    push_subscriptions = PushSubscription.query.all()
    for push_subscription in push_subscriptions:
        channel = sub_webpush(sub_user_channel(push_subscription.user_id))
        redis.set(channel, json.dumps(push_subscription.subscription_json))


def change_user_role(current_user_id: int, user_id: int, admin: bool = True) -> Dict:
    """Admin will change user's role."""

    user = get_a_user(user_id)

    errors = dict()
    if current_user_id == user_id:
        errors['sender'] = "Sender cannot change his role by himself."
    if user.admin == admin:
        errors['user_id'] = f"This user cannot be changed to {'admin' if admin else 'normal'}."
    if errors:
        e = BadRequest()
        e.data = dict(
            errors=errors,
            message='Input payload validation failed'
        )
        raise e

    try:
        user.admin = admin
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to save your data.")

    data = dict(
        type=TYPE_NOTIFICATION_ADMIN_USER,
        message="You become an admin." if admin else "You become a normal.",
        data=dict(user_id=user_id, admin=admin)
    )
    notify_one_user(user_id, data, TYPE_NOTIFICATION_ACTION_USER)

    return dict(message="You successfully changed user's role")


def archive_user(current_user_id: int, user_id: int, archive: bool = True) -> Dict:
    """Admin will archive/unarchive the user."""

    user = get_a_user(user_id)

    errors = dict()
    if current_user_id == user_id:
        errors['sender'] = "Sender cannot change his archive by himself."
    if user.archived == archive:
        errors['user_id'] = f"This user cannot be changed to {'archive' if archive else 'unarchive'}."
    if errors:
        e = BadRequest()
        e.data = dict(
            errors=errors,
            message='Input payload validation failed'
        )
        raise e

    try:
        user.archived = archive
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to save your data.")

    if archive:
        # Notify
        data = dict(
            type=TYPE_NOTIFICATION_ARCHIVE_USER,
            message="You was archived.",
            data=dict(user_id=user_id, archive=archive)
        )
        notify_one_user(user_id, data, TYPE_NOTIFICATION_ACTION_USER)

        # remove channel
        channels = redis.scan(match=f'*:{sub_user_channel(user_id)}')
        if channels:
            redis.delete(*channels)

        push_subscription = PushSubscription.query.filter_by(user_id=user_id).first()
        if push_subscription:
            delete_data(push_subscription)
    else:
        try:
            html_content = f'''
<div class="email-container">
    <h1>{current_app.config['APPLICATION']}</h1>
    <p>Hello <em>@{user.username}</em>, we received a request to unarchive your account.</p>
    <p>You will now be able to connect to our app with your account.</p>
    <p>If you do not want to unarchive your account, please send an email to : <em>{current_app.config['MAIL_DEFAULT_SENDER']}</em>.</p>
</div>
{STYLE_HTML}
            '''
            msg = EmailMultiAlternatives(
                subject='Unarchived your account',
                body=f"{current_app.config['APPLICATION']}\n"
                     f"Hello @{user.username}, we received a request to unarchive your account.\n"
                     f"You will now be able to connect to our app with your account."
                     f"If you do not want to unarchive your account, please send an email to : {current_app.config['MAIL_DEFAULT_SENDER']}.",
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            current_app.logger.error(str(e), exc_info=True)
            raise InternalServerError("The server encountered an internal error and was unable to send your email.")

    return dict(message=f"You successfully {'archived' if archive else 'unarchived'} this user.")


def notify_one_user(user_id: int, data, type_publish: str = None) -> None:
    """
    Send notification to the user.

    :param user_id: The receiver's id
    :param data: The data want to be sent
    :param type_publish: The event type.
    """

    channel = sub_user_channel(user_id)
    publish(channel, data, type_publish)
