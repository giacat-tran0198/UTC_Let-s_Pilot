"""Socket endpoint definitions for /ws/messages namespace."""

from flask import request
from flask_restx import marshal
from flask_socketio import Namespace

from src.chat.dto.message_dto import message_item
from src.chat.service.message_service import (save_new_message, valid_input_room, valid_input_message,
                                              notify_new_message_into_members_offline)
from src.chat.service.ws_service import (save_user_id_with_sid, get_user_id_by_sid,
                                         user_join_into_project, user_leave_from_project, get_sid_by_user_id_in_room)
from src.chat.util.decorator import token_required


class WsMessageNamespace(Namespace):

    @token_required
    def on_connect(self):
        """Event connect with allow to access the headers from the current request."""
        save_user_id_with_sid(self.on_connect.current_user_id)

    def on_join_project(self, data):
        """Event join in project if the user log into the conversation."""

        # Verify the project's id
        data = valid_input_room(data)

        # The user enter the room
        self.enter_room(request.sid, data.get('room'))

        # Add one user online in project
        user_id = get_user_id_by_sid()
        list_online = user_join_into_project(data.get('room'))

        # Notify the others users one new user join in project
        self.emit('online', data=dict(user_id=user_id), room=data.get('room'), include_self=False)

        return list_online

    def on_leave_project(self):
        """Event leave from project if the user exit from the conversation."""

        # one user leave from project
        data_leave = user_leave_from_project()

        # Verify his room
        if data_leave and data_leave.get('room'):
            self.leave_room(data_leave.get('sid'), data_leave.get('room'))

            # Notify the others users one user leave from project
            self.emit('offline', data=dict(user_id=data_leave.get('user_id')), room=data_leave.get('room'),
                      include_self=False)

    def on_send_message(self, data):
        """Event the user send a message in the conversation."""

        # Verify the message data
        data = valid_input_message(data)
        data['sender_id'] = get_user_id_by_sid()

        # Save this message
        message = save_new_message(data)
        message_dto = marshal(message, message_item, skip_none=True)

        if not message.receiver_id:
            # Send the public message
            self.emit('receive_message', data=message_dto, room=data.get('room'), include_self=False)
            notify_new_message_into_members_offline(message=message, room=data.get('room'))
        else:
            # Send the private message
            sid_receive = get_sid_by_user_id_in_room(user_id=message.receiver_id, room=data.get('room'))
            if sid_receive:
                self.emit('receive_message', data=message_dto, room=sid_receive, include_self=False)
            else:
                notify_new_message_into_members_offline(message=message, only_receiver=True)

        return message_dto

    def on_disconnect(self):
        """Event disconnect suddenly."""
        self.on_leave_project()
