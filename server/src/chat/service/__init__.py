"""Service logic for data."""

from flask import current_app
from werkzeug.exceptions import InternalServerError

from src.chat import db


def save_data(data) -> None:
    """Save the object."""

    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to save your data.")


def insert_data(query, data) -> None:
    """Insert data by query."""

    try:
        db.session.execute(query.insert(), data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to save your data.")


def delete_data(data) -> None:
    """Delete the object."""

    try:
        db.session.delete(data)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to delete your data.")
