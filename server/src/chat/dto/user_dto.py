"""The definition for User schema."""

from flask_cors import cross_origin
from flask_restx import Namespace, fields

from src.chat.util.pagination import list_model, params

api = Namespace('user_v1', description='user related operations',
                decorators=[cross_origin()])

user_post = api.schema_model('User_Post', {
    'required': ['email', 'username', 'password', 'first_name', 'last_name'],
    'properties': {
        'email': {
            'type': 'string',
            'format': 'email',
        },
        'username': {
            'type': 'string',
        },
        'password': {
            'type': 'string',
        },
        'first_name': {
            'type': 'string',
        },
        'last_name': {
            'type': 'string',
        },
        'ava': {
            'type': 'string'
        }
    },
    'type': 'object',
})

user_put = api.schema_model('User_Put', {
    'required': ['username', 'first_name', 'last_name'],
    'properties': {
        'username': {
            'type': 'string',
        },
        'first_name': {
            'type': 'string',
        },
        'last_name': {
            'type': 'string',
        },
        'ava': {
            'type': 'string'
        }
    },
    'type': 'object',
})

user_password = api.schema_model('User_Password', {
    'required': ['older_password', 'new_password'],
    'properties': {
        'older_password': {
            'type': 'string',
        },
        'new_password': {
            'type': 'string',
        },
    },
    'type': 'object',
})

user_forget_password = api.schema_model('User_Forget_Password', {
    'required': ['email'],
    'properties': {
        'email': {
            'type': 'string',
            'format': 'email',
            'pattern': r'\S+@\S+.\S+',
        },
    },
    'type': 'object',
})

user_item = api.model('User_Item', {
    'id': fields.Integer(description="user's identifier"),
    'email': fields.String(description='user email address'),
    'username': fields.String(description='user username'),
    'first_name': fields.String(description="user's first name"),
    'last_name': fields.String(description="user's last name"),
    'ava': fields.String(description="user's ava in base64"),
    'admin': fields.Boolean(description="user's role"),
    'archived': fields.Boolean(description="user archived")
})

user_list = api.model('User_List', model=list_model(user_item))

user_params = params.copy()
user_params['filter_by'] = {'in': 'query', 'description': 'The filter for email, first name, last name, ou username',
                            'type': 'string'}

subscription_info = api.model('Subscription_info', {
    'endpoint': fields.String(required=True),
    'expirationTime': fields.Integer,
    'keys': fields.Nested(api.model('Subscription_info_keys', {
        'p256dh': fields.String(required=True),
        'auth': fields.String(required=True)
    }))
})

token_parser = api.parser()
token_parser.add_argument('token', required=True, help="User's Token!")