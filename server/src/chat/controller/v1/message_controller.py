"""API endpoint definitions for /messages namespace."""

from http import HTTPStatus

from flask_restx import Resource

from src.chat.dto.message_dto import api, message_list, message_params
from src.chat.service.message_service import get_all_messages
from src.chat.util.decorator import token_required


@api.route('/<int:project_id>')
class List(Resource):
    """Collection for Message in Project"""

    @token_required
    @api.doc('List of message', params=message_params, security='Bearer')
    @api.response(int(HTTPStatus.OK), 'Collection for projects.', message_list, skip_none=True)
    @api.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), 'Error internal server.')
    @api.response(int(HTTPStatus.UNAUTHORIZED), 'Unauthorized.')
    @api.response(int(HTTPStatus.FORBIDDEN), 'Provide a valid auth token.')
    @api.marshal_with(message_list, skip_none=True)
    def get(self, project_id: int):
        """List all registered message in project."""
        return get_all_messages(user_id=self.get.current_user_id, project_id=project_id)
