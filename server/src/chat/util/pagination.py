"""Simple helper to paginate query"""

from flask import url_for, request
from flask_restx import fields
from flask_sqlalchemy import BaseQuery

from src.chat.model.pagination import Pagination


def extract_pagination(page=None, per_page=None, **request_args):
    """Get extract page and per_page"""
    page = int(page) if page is not None else Pagination.DEFAULT_PAGE_NUMBER
    per_page = int(per_page) if per_page is not None else Pagination.DEFAULT_PAGE_SIZE
    return page, per_page, request_args


def paginate(query: BaseQuery) -> Pagination:
    """Get a pagination and data's object from Query"""
    page, per_page, other_request_args = extract_pagination(**request.args)
    page_obj = query.paginate(page=page, per_page=per_page)
    next_ = url_for(
        request.endpoint,
        page=page_obj.next_num if page_obj.has_next else page_obj.page,
        per_page=per_page,
        **other_request_args,
        **request.view_args
    )
    prev = url_for(
        request.endpoint,
        page=page_obj.prev_num if page_obj.has_prev else page_obj.page,
        per_page=per_page,
        **other_request_args,
        **request.view_args
    )

    return Pagination(
        total=page_obj.total,
        pages=page_obj.pages,
        has_prev=page_obj.has_prev,
        has_next=page_obj.has_next,
        next_=next_,
        prev=prev,
        data=page_obj.items
    )


def list_model(data):
    """Model for collection data"""
    return {
        'total': fields.Integer(description='The total number of items'),
        'pages': fields.Integer(description='The total number of pages'),
        'has_next': fields.Boolean(description='True if a next page exists'),
        'has_prev': fields.Boolean(description='True if a previous page exists'),
        'next': fields.String(description='A pagination for the next page'),
        'prev': fields.String(description='A pagination object for the previous page'),
        'data': fields.List(fields.Nested(data, allow_null=True, skip_none=True),
                            description='The items for the current page'),
    }


params = {
    'page': {'in': 'query', 'description': 'The current page number', 'default': Pagination.DEFAULT_PAGE_NUMBER,
             'type': 'integer'},
    'per_page': {'in': 'query', 'description': 'The number of items to be displayed on a page',
                 'default': Pagination.DEFAULT_PAGE_SIZE,
                 'type': 'integer'}
}
