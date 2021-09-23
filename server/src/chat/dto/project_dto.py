"""The definition for Project schema."""

from flask_cors import cross_origin
from flask_restx import Namespace, fields

from src.chat.dto.user_dto import user_item
from src.chat.util.pagination import list_model, params

api = Namespace('project_v1', description='Project related operations',
                decorators=[cross_origin()])

project_post = api.model('Project_Post', {
    'title': fields.String(required=True),
    'coaches': fields.List(fields.Integer(description="User's identify")),
    'participants': fields.List(fields.Integer(description="User's identify"))
})

project_put = api.model('Project_Put', {
    'title': fields.String(required=True),
})

project_participant = api.model('Project_Participant', {
    'participant': fields.Integer(description="User's identify", required=True)
})

project_designate_coach = api.model('Project_Designate_New_Coach', {
    'coach': fields.Integer(description="User's identify")
})

project_item = api.model('Project_Item', {
    'id': fields.Integer(description="Project's identifier"),
    'title': fields.String,
    'owner': fields.Nested(user_item, description="Project's owner"),
    'coaches': fields.List(fields.Nested(user_item), description='List for coach'),
    'participants': fields.List(fields.Nested(user_item), description='List for participant'),
})

project_list = api.model('Project_List', model=list_model(project_item))

project_params = params.copy()
project_params['filter_by'] = {'in': 'query', 'description': 'The filter for title.', 'type': 'string'}
