"""API endpoint definitions for /users namespace."""

from http import HTTPStatus

from flask import request, current_app
from flask_restx import Resource

from src.chat.dto.auth_dto import auth_resp
from src.chat.dto.user_dto import (api, user_item, user_list, user_post, user_params, user_put, user_password,
                                   user_forget_password, subscription_info, token_parser)
from src.chat.service.user_service import (save_new_user, get_all_users, get_a_user, update_a_user,
                                           update_a_user_password, update_password_forgotten,
                                           save_data_subscription_webpub, unsubscription_data_subscription_webpub,
                                           change_user_role, archive_user)
from src.chat.util.decorator import token_required, decode_auth_token, admin_token_required
from src.chat.util.stream import stream, disconnect_sse


@api.route('/')
class List(Resource):
    """Collection for Users."""

    @token_required
    @api.doc('List_of_registered_users', params=user_params, security='Bearer')
    @api.response(int(HTTPStatus.OK), 'Collection for users.', user_list)
    @api.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), 'Error internal server.')
    @api.response(int(HTTPStatus.UNAUTHORIZED), 'Unauthorized.')
    @api.response(int(HTTPStatus.FORBIDDEN), 'Provide a valid auth token.')
    @api.marshal_with(user_list)
    def get(self):
        """List all registered users."""
        filter_by = request.args.get('filter_by')
        return get_all_users(filter_by)

    @api.response(int(HTTPStatus.CREATED), 'User successfully created.', auth_resp)
    @api.response(int(HTTPStatus.CONFLICT), 'User already exists.')
    @api.doc('Create a new user')
    @api.expect(user_post, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)


@api.route('/me')
class Me(Resource):
    """My Profile."""

    @token_required
    @api.doc('Get my profile', security='Bearer')
    @api.response(int(HTTPStatus.OK), 'Successfully get my profile.', user_item)
    @api.marshal_with(user_item)
    def get(self):
        """Get all user's profile by herself."""
        return get_a_user(self.get.current_user_id)

    @token_required
    @api.doc('Edit my profile', security='Bearer')
    @api.expect(user_put, validate=True)
    @api.response(int(HTTPStatus.OK), 'Successfully edit my profile.')
    @api.response(int(HTTPStatus.BAD_REQUEST), 'Error.')
    @api.response(int(HTTPStatus.NOT_FOUND), 'Error not me.')
    @api.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), 'Error saving data.')
    def put(self):
        """Edit your profile."""
        data = request.json
        return update_a_user(self.put.current_user_id, data)


@api.route('/me/reset-password', endpoint='user_v1_reset_password')
class Me_Reset_Password(Resource):
    """Reset my password."""

    @token_required
    @api.doc('Edit my password', security='Bearer')
    @api.expect(user_password, validate=True)
    @api.response(int(HTTPStatus.OK), 'Successfully edit my password.')
    @api.response(int(HTTPStatus.BAD_REQUEST), 'Error edit my password.')
    @api.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), 'Error saving data.')
    def put(self):
        """Edit your password."""
        data = request.json
        return update_a_user_password(self.put.current_user_id, data)


@api.route('/me/forget-password', endpoint='user_v1_forget_password')
class Me_Forget_Password(Resource):
    """Forget my password."""

    @api.doc('Forgot my password')
    @api.expect(user_forget_password, validate=True)
    @api.response(int(HTTPStatus.OK), 'Successfully send new password.')
    @api.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), 'Error saving data.')
    def post(self):
        """Send email new random password"""
        data = request.json
        return update_password_forgotten(data['email'])


@api.route('/stream')
class Stream(Resource):
    """Stream SSE"""

    @api.doc('Connect the stream SSE')
    @api.expect(token_parser)
    def get(self):
        """Connect the stream SSE."""
        token = token_parser.parse_args()['token']
        user_id, _ = decode_auth_token(token)
        return stream(user_id)

    @token_required
    @api.doc('Delete channel in stream SSE', security='Bearer')
    def delete(self):
        """Delete channel in stream SSE"""
        disconnect_sse(user_id=self.delete.current_user_id)
        return ''


@api.route('/subscription')
class PubSub(Resource):
    """Webpush"""

    @api.doc('Get public key', security='Bearer')
    @token_required
    def get(self):
        """Get the public key for Service Worker"""
        return dict(public_key=current_app.config['VAPID_PUBLIC_KEY'])

    @api.doc('Store client key', security='Bearer')
    @api.expect(subscription_info, validate=True)
    @token_required
    def post(self):
        """Store the key of Service Worker"""
        data = request.json
        return save_data_subscription_webpub(data, self.post.current_user_id)

    @api.doc('Unsubscription client key', security='Bearer')
    @token_required
    def delete(self):
        """Unsubscription the key of Service Worker"""
        return unsubscription_data_subscription_webpub(self.delete.current_user_id)


@api.route('/admin/<int:user_id>')
class Admin(Resource):
    """Some admin's functions."""

    @api.doc("Change user's role to admin", security='Bearer')
    @admin_token_required
    def post(self, user_id: int):
        """Change user's role to admin."""
        return change_user_role(self.post.current_user_id, user_id)

    @api.doc("Change user's role to normal", security='Bearer')
    @admin_token_required
    def delete(self, user_id: int):
        """Change user's role to normal."""
        return change_user_role(self.delete.current_user_id, user_id, False)


@api.route('/archive/<int:user_id>')
class Archive(Resource):
    """Archive one user."""

    @api.doc("Archive user", security='Bearer')
    @admin_token_required
    def post(self, user_id: int):
        """Admin archive user."""
        return archive_user(self.post.current_user_id, user_id)

    @api.doc("Change user's role to normal", security='Bearer')
    @admin_token_required
    def delete(self, user_id: int):
        """Admin unarchive user."""
        return archive_user(self.delete.current_user_id, user_id, False)
