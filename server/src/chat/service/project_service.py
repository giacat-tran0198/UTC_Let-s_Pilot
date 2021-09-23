"""Service logic for project """

from typing import Dict, List

from flask import current_app
from flask_restx import marshal
from werkzeug.exceptions import Conflict, Forbidden, InternalServerError, BadRequest

from src.chat import db
from src.chat.dto.project_dto import project_item, user_item
from src.chat.model.pagination import Pagination
from src.chat.model.project import Project, user_coaches_to_project, user_participates_of_project
from src.chat.model.user import User
from src.chat.service import save_data, insert_data, delete_data
from src.chat.service.user_service import get_a_user, notify_one_user
from src.chat.util.constant import *
from src.chat.util.pagination import paginate


def save_new_project(user_id: int, data: Dict) -> Project:
    """
    Save a new project with data

    :param user_id: The user's id
    :param data: Dict['title', 'participants', 'coaches']
    :return: Project
    """

    project = Project.query.filter_by(title=data['title']).first()
    if project:
        raise Conflict('Project already exists. Please create new other project.')

    new_project = Project(
        title=data['title'],
        owner_id=user_id,
    )
    save_data(new_project)

    # Remove user duple of participants in coaches
    participants = list(set(data.get('participants', [])) - set(data.get('coaches', [])))
    if participants:
        insert_participants(id_project=new_project.id, participants=participants)
    if data.get('coaches'):
        insert_coaches(id_project=new_project.id, coaches=data.get('coaches'))

    # Notify
    data = {'type': TYPE_NOTIFICATION_ADD_INTO_PROJECT,
            'message': f"'@{new_project.owner.username}' created a new project '{new_project.title}'. "
                       f"You are invited to join it.",
            'data': marshal(new_project, project_item)}
    notify_all_member_in_project(users_id=new_project.get_id_members(), data=data,
                                 type_publish=TYPE_NOTIFICATION_ACTION_PROJECT,
                                 exclude_users_id=[user_id])

    return new_project


def get_all_projects(user_id: int, filter_by) -> Pagination:
    """
    Get all user's project.

    :param user_id: The user's id
    :param filter_by: The key want to filter
    :return: Pagination for project
    """

    query = Project.query.filter((Project.owner_id == user_id)
                                 | (Project.coaches.any(User.id == user_id))
                                 | (Project.participants.any(User.id == user_id))
                                 )

    if filter_by:
        query = query.filter(Project.title.like(f'%{filter_by}%'))

    return paginate(query)


def get_project_item(id_project: int) -> Project:
    """
    Find project with its id.

    :param id_project: the project's id
    :return: Project
    """

    return Project.query.filter_by(id=id_project).first_or_404('Project Not Found')


def update_project(user_id: int, id_project: int, data: Dict) -> Project:
    """
    Update project with new data

    :param user_id: The user's id
    :param id_project: The project's id want to be modified.
    :param data: Dict['title']
    :return: Project
    """

    project = get_project_item(id_project)
    required_own_project(user_id, project)

    older_project_title = project.title

    try:
        project.title = data['title']
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to save your data.")

    else:
        # Notify
        data = dict(
            type=TYPE_NOTIFICATION_EDIT_PROJECT,
            message=f"The title's project '{older_project_title}' become the new title '{project.title}'.",
            data=dict(project_id=project.id, project_title=project.title)
        )
        notify_all_member_in_project(users_id=project.get_id_members(), data=data,
                                     type_publish=TYPE_NOTIFICATION_ACTION_PROJECT,
                                     exclude_users_id=[user_id])

    return project


def delete_project(user_id: int, id_project: int) -> Dict:
    """
    Delete project.

    :param user_id: The user's id.
    :param id_project: The project's id want to be removed.
    :return: message notification
    """

    project = get_project_item(id_project)
    required_own_project(user_id, project)
    older_project_title = project.title
    older_project_id = project.id
    owner_username = project.owner.username
    owner_id = project.owner_id
    members_id = project.get_id_members()

    delete_data(project)

    # Notify
    data = dict(
        type=TYPE_NOTIFICATION_DELETE_PROJECT,
        message=f"The project '{older_project_title}' was removed by '@{owner_username}'.",
        data=dict(project_id=older_project_id, project_title=older_project_title),
    )
    notify_all_member_in_project(users_id=members_id, data=data, type_publish=TYPE_NOTIFICATION_ACTION_PROJECT,
                                 exclude_users_id=[owner_id])

    return dict(message='Your project was successfully removed.')


def invite_participant_into_project(user_id: int, id_project: int, data: Dict) -> User:
    """
    Invite new member into project.

    :param user_id: The user's id
    :param id_project: The project's id want to be added
    :param data: Dict['participant']
    :return: User
    """

    project = get_project_item(id_project)

    required_member_in_project(user_id=user_id, project=project)

    participant = get_a_user(data.get('participant'))

    # check new user exist project ou non
    if participant.id in project.get_id_members():
        e = BadRequest()
        e.data = dict(
            errors=dict(participant="You can't add an existing project member."),
            message='Input payload validation failed.'
        )
        raise e

    insert_participants(id_project=project.id, participants=[data.get('participant')])

    # Notify to new participant
    data = dict(
        type=TYPE_NOTIFICATION_ADD_INTO_PROJECT,
        message=f"You was invited into the project '{project.title}'.",
        data=marshal(project, project_item)
    )
    notify_one_user(user_id=participant.id, data=data, type_publish=TYPE_NOTIFICATION_ACTION_PROJECT)

    # Notify to other members
    data = dict(
        type=TYPE_NOTIFICATION_ADD_INTO_PROJECT,
        message=f"The new participant '@{participant.username}' was added into the project '{project.title}'.",
        data=marshal(participant, user_item)
    )
    notify_all_member_in_project(users_id=project.get_id_members(), data=data,
                                 type_publish=TYPE_NOTIFICATION_ACTION_PROJECT,
                                 exclude_users_id=[user_id, participant.id])

    return participant


def leave_from_project(user_id: int, id_project: int) -> Dict:
    """
    A member want to leave from project

    :param user_id: The user's id
    :param id_project: The project's id which user want to leave
    :return: message
    """

    project = get_project_item(id_project)
    current_user = get_a_user(user_id)

    required_member_in_project(user_id=user_id, project=project)

    if project.owner == current_user:
        e = BadRequest()
        e.data = dict(
            errors=dict(owner="The owner can't leave the project."),
            message='Request failed.'
        )
        raise e

    try:
        if current_user in project.coaches:
            project.coaches.remove(current_user)
        elif current_user in project.participants:
            project.participants.remove(current_user)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to remove your data.")

    else:
        # Notify
        data = dict(
            type=TYPE_NOTIFICATION_EDIT_PROJECT,
            message=f"'@{current_user.username}' left the project'{project.title}'.",
            data=dict(user_id=user_id, project_id=project.id, project_title=project.title)
        )
        notify_all_member_in_project(users_id=project.get_id_members(), data=data,
                                     type_publish=TYPE_NOTIFICATION_ACTION_PROJECT,
                                     exclude_users_id=[user_id])

    return dict(message='You left the project.')


def designate_coach_into_project(user_id: int, id_project: int, data: Dict) -> Dict:
    """
    Owner or coach designate a participant becoming to be new coach.

    :param user_id: The user's id
    :param id_project: The project's which user want to designate a member
    :param data: Dict['coach']
    :return: message
    """

    project = get_project_item(id_project)
    required_own_or_coach_in_project(user_id=user_id, project=project)
    coach = get_a_user(data.get('coach'))

    if coach == project.owner or coach in project.coaches:
        e = BadRequest()
        e.data = dict(
            errors=dict(coach="You can't add an owner or a coach become a new coach."),
            message='Input payload validation failed.'
        )
        raise e

    if coach not in project.participants:
        e = BadRequest()
        e.data = dict(
            errors=dict(coach="You can't add a not member become a new coach."),
            message='Input payload validation failed.'
        )
        raise e

    try:
        # Remove them from list participants
        project.participants.remove(coach)

        # Add them into list coaches
        project.coaches.append(coach)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to remove your data.")

    else:
        # Notify to new coach
        data = dict(
            type=TYPE_NOTIFICATION_EDIT_PROJECT,
            message=f"You was designated new coach in the project '{project.title}'.",
            data=dict(project_id=project.id, project_title=project.title),
        )
        notify_one_user(user_id=coach.id, data=data, type_publish=TYPE_NOTIFICATION_ACTION_PROJECT)

        # Notify to the other members
        data = dict(
            type=TYPE_NOTIFICATION_EDIT_PROJECT,
            message=f"'@{coach.username}' was designated new coach in the project '{project.title}'.",
            data=dict(user_id=coach.id, project_id=project.id, project_title=project.title)
        )
        notify_all_member_in_project(users_id=project.get_id_members(), data=data,
                                     type_publish=TYPE_NOTIFICATION_ACTION_PROJECT,
                                     exclude_users_id=[user_id, coach.id])

    return dict(message='You designated a new coach.')


def withdraw_coach_in_project(user_id: int, id_project: int, data: Dict) -> Dict:
    """
    Owner or coach withdraw a coach become be participant.

    :param user_id: The user's id
    :param id_project: The project's id which user want to withdraw a coach
    :param data: Dict['coach']
    :return: message
    """

    project = get_project_item(id_project)
    required_own_or_coach_in_project(user_id=user_id, project=project)
    coach = get_a_user(data.get('coach'))

    if coach == project.owner or coach not in project.coaches:
        e = BadRequest()
        e.data = dict(
            errors=dict(coach="You can't withdraw a not coach become a participant."),
            message='Input payload validation failed.'
        )
        raise e

    try:
        # Remove them from list coaches
        project.coaches.remove(coach)

        # Add them into list participant
        project.participants.append(coach)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to remove your data.")

    else:
        # Notify to new participant
        data = dict(
            type=TYPE_NOTIFICATION_EDIT_PROJECT,
            message=f"You was withdrawn from coach in the project '{project.title}'.",
            data=dict(project_id=project.id, project_title=project.title),
        )
        notify_one_user(user_id=coach.id, data=data, type_publish=TYPE_NOTIFICATION_ACTION_PROJECT)

        # Notify to the other members
        data = dict(
            type=TYPE_NOTIFICATION_EDIT_PROJECT,
            message=f"'@{coach.username}' was withdrew from coach, he will be a participant the project'{project.title}'.",
            data=dict(user_id=coach.id, project_id=project.id, project_title=project.title)
        )
        notify_all_member_in_project(users_id=project.get_id_members(), data=data,
                                     type_publish=TYPE_NOTIFICATION_ACTION_PROJECT,
                                     exclude_users_id=[user_id, coach.id])

    return dict(message='You withdrew a coach. He will be a participant.')


def remove_participant_in_project(user_id: int, id_project: int, data: Dict) -> Dict:
    """
    Owner or coach remove a participant from project.

    :param user_id: The user's id
    :param id_project: The project's id which user want to remove a member
    :param data: Dict['participant']
    :return: message
    """

    project = get_project_item(id_project)
    required_own_or_coach_in_project(user_id=user_id, project=project)
    participant = get_a_user(data.get('participant'))

    if is_owner(user_id=participant.id, project=project) or is_coach(user_id=participant.id, project=project):
        e = BadRequest()
        e.data = dict(
            errors=dict(participant="You can't remove an owner or coach from project."),
            message='Input payload validation failed.'
        )
        raise e

    if not is_participant(user_id=participant.id, project=project):
        e = BadRequest()
        e.data = dict(
            errors=dict(participant="You can't remove a not member from project."),
            message='Input payload validation failed.'
        )
        raise e

    try:
        # Remove them from list participants
        project.participants.remove(participant)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e), exc_info=True)
        raise InternalServerError("The server encountered an internal error and was unable to remove your data.")

    else:
        # Notify to this member
        data = dict(
            type=TYPE_NOTIFICATION_EDIT_PROJECT,
            message=f"You was removed in the project '{project.title}'.",
            data=dict(project_id=project.id, project_title=project.title),
        )
        notify_one_user(user_id=participant.id, data=data, type_publish=TYPE_NOTIFICATION_ACTION_PROJECT)

        # Notify to the other members
        data = dict(
            type=TYPE_NOTIFICATION_EDIT_PROJECT,
            message=f"'@{participant.username}' was removed in the project '{project.title}'.",
            data=dict(user_id=participant.id, project_id=project.id, project_title=project.title)
        )
        notify_all_member_in_project(users_id=project.get_id_members(), data=data,
                                     type_publish=TYPE_NOTIFICATION_ACTION_PROJECT,
                                     exclude_users_id=[user_id, participant.id])

    return dict(message='You removed a participant.')


def required_own_project(user_id: int, project: Project) -> None:
    """
    Check user is owner.

    :param user_id: The user's id
    :param project: Project
    """

    if project.owner_id != user_id:
        raise Forbidden("You must be the project's owner.")


def required_own_or_coach_in_project(user_id: int, project: Project) -> None:
    """
    Check user is owner or coach.

    :param user_id: The user's id
    :param project: Project
    """

    if not (is_owner(user_id, project) or is_coach(user_id, project)):
        raise Forbidden("Yous must be an project's owner or coach.")


def required_member_in_project(user_id: int, project: Project) -> None:
    """
    Check user is member.

    :param user_id: The user's id
    :param project: Project
    """

    if not (is_owner(user_id, project) or is_coach(user_id, project) or is_participant(user_id, project)):
        raise Forbidden("You must be a project's member.")


def insert_participants(id_project: int, participants: List[int]) -> None:
    """
    Add list participants into project.

    :param id_project: The project's id want to be added new participants.
    :param participants: List[int]
    """

    data_participant = list(dict(user_id=i, project_id=id_project) for i in participants)
    insert_data(user_participates_of_project, data_participant)


def insert_coaches(id_project: int, coaches: List[int]) -> None:
    """
    Add list coaches into project.

    :param id_project: The project's id want to be added new coaches
    :param coaches: List[int]
    """

    data_participant = list(dict(user_id=i, project_id=id_project) for i in coaches)
    insert_data(user_coaches_to_project, data_participant)


def is_owner(user_id: int, project: Project) -> bool:
    """Verify the user is an owner."""

    return project.owner_id == user_id


def is_coach(user_id: int, project: Project) -> bool:
    """Verify the user is a coach."""

    return any(user_id == user.id for user in project.coaches)


def is_participant(user_id: int, project: Project) -> bool:
    """Verify the user is a participant."""

    return any(user_id == user.id for user in project.participants)


def notify_all_member_in_project(users_id: List[int], data, type_publish: str = None,
                                 exclude_users_id: List[int] = None) -> None:
    """Notify all the member in project."""

    if exclude_users_id:
        users_id = list(set(users_id) - set(exclude_users_id))
    for user_id in users_id:
        notify_one_user(user_id, data, type_publish)
