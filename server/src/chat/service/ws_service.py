"""Service logic for socket."""

import json
from typing import List, Optional, Dict

from flask import request

from src.chat import redis


def save_user_id_with_sid(user_id: int) -> None:
    """Save the user's id with key user's sid in Redis."""

    data = dict(user_id=user_id)
    redis.set(_get_sid_channel(), json.dumps(data))


def delete_user_id_by_sid() -> Dict:
    """
    Delete the data with key user's sid in Redis.

    :return: Dict[user_id, sid, room]
    """

    channel = _get_sid_channel()
    data = redis.get(channel)
    redis.delete(channel)
    return _transfer_data(data)


def get_user_id_by_sid() -> Optional[int]:
    """
    Get user's from sid.

    :return: None|user_id
    """

    data = redis.get(_get_sid_channel())
    if data:
        data = _transfer_data(data)
        return data.get('user_id')
    return None


def get_sid_by_user_id_in_room(user_id: int, room: str) -> Optional[str]:
    """
    Get sid from user's id in his chatting room.

    :param user_id: The user's id
    :param room: The room's name
    :return: None|sid
    """

    data = redis.sscan(room, 0, f'*user_id*{user_id}*')[1]
    return _transfer_data(data[len(data) - 1]).get('sid') if data else None


def get_all_user_in_room(room: str) -> List:
    """Get all user online in room."""

    return [_transfer_data(x) for x in redis.smembers(room)]


def user_join_into_project(room: str) -> List:
    """
    The user join in to project.

    :param room: The room's name
    :return: List user's id online in room
    """

    data = json.dumps(
        dict(
            user_id=get_user_id_by_sid(),
            sid=request.sid,
            room=room
        ),
        sort_keys=True
    )
    redis.sadd(room, data)
    redis.set(_get_sid_channel(), data)

    return [dict(user_id=x.get('user_id')) for x in get_all_user_in_room(room)]


def user_leave_from_project() -> Dict:
    """
    Delete the user's data by sid in Redis.

    :return: Dict[user_id, sid, room]
    """

    channel = _get_sid_channel()
    data = redis.get(channel)

    # remove user's sid
    redis.delete(channel)

    if data:
        data = _transfer_data(data)

        # remove user's room
        if data.get('room'):
            redis.srem(data.get('room'), json.dumps(data, sort_keys=True))

    return data


def _get_sid_channel() -> str:
    """Create channel sid in Redis."""

    return f'sid:{request.sid}'


def _transfer_data(data) -> Dict:
    """Transfer data into form type Dict"""

    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return json.loads(data)
