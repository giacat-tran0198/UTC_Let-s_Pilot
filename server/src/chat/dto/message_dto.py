"""The definition for Message schema."""

from flask_cors import cross_origin
from flask_restx import Namespace, fields

from src.chat.dto.user_dto import user_item
from src.chat.util.pagination import list_model, params

api = Namespace('message_v1', description='Message related operations',
                decorators=[cross_origin()])

message_post = api.model('Message_Post', {
    'content': fields.String(required=True),
    'receiver': fields.Integer(description="User's identify. Only owner or coach determine."),
})

message_item = api.model('Message_Item', {
    'id': fields.Integer(description="Message's identifier"),
    'content': fields.String,
    'file_name': fields.String,
    'file_base64': fields.String,
    'sender': fields.Nested(user_item, description="Message's owner"),
    'receiver': fields.Nested(user_item, description="Message's receiver", skip_none=True, allow_null=True),
    'created_at': fields.String
})

message_list = api.model('Project_List', model=list_model(message_item))

message_params = params.copy()
