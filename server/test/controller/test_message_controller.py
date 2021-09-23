import json
import unittest

from flask import url_for

from src.chat import db
from src.chat.model.message import Message
from src.chat.model.project import Project
from src.chat.model.user import User
from src.chat.service.auth_service import encode_auth_token
from test.base import BaseTestCase


# def register_message(client, token: str, project_id: int, data: Dict):
#     return client.post(
#         url_for('api.message_v1_list', project_id=project_id),
#         data=json.dumps(data),
#         headers=dict(Authorization='Bearer ' + token),
#         content_type='application/json'
#     )


def api_message_list(client, token: str, project_id: int):
    return client.get(
        url_for('api.message_v1_list', project_id=project_id),
        headers=dict(Authorization='Bearer ' + token),
        content_type='application/json'
    )


class TestMessageController(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.seed()

    def seed(self):
        # sender
        self.sender = User(
            email='sender@test.com',
            password='test',
            username='username',
            first_name='first name',
            last_name='last name',
        )
        db.session.add(self.sender)

        # Coaches
        self.coach = User(
            email='coach@test.com',
            password='test',
            username='coach',
            first_name='first name',
            last_name='last name',
        )
        db.session.add(self.coach)

        # Participants
        self.participant = User(
            email='participant@test.com',
            password='test',
            username='participant',
            first_name='first name',
            last_name='last name',
        )

        db.session.add(self.participant)

        # Project
        self.project = Project(
            title='project0',
            owner=self.sender
        )
        db.session.add(self.project)

        self.project.coaches.append(self.coach)
        self.project.participants.append(self.participant)

        # Message
        self.messages = []
        self.messages.append(Message(
            content='message 1',
            sender=self.sender,
            project=self.project
        ))
        self.messages.append(Message(
            content='message 2',
            sender=self.coach,
            project=self.project
        ))
        self.messages.append(Message(
            content='message 3',
            sender=self.participant,
            project=self.project
        ))
        self.messages.append(Message(
            content='message 4',
            sender=self.participant,
            project=self.project
        ))
        self.messages.append(Message(
            content='message 5',
            sender=self.sender,
            receiver=self.coach,
            project=self.project
        ))
        self.messages.append(Message(
            content='message 6',
            sender=self.coach,
            receiver=self.participant,
            project=self.project
        ))

        db.session.commit()

    def test_get_all_message_public_and_private(self):
        # From sender
        token, _ = encode_auth_token(self.sender.id)
        response = api_message_list(self.client, token, self.project.id)
        self.assert200(response)

        response = json.loads(response.data)
        self.assertEqual(5, response['total'])

        # From coach
        token, _ = encode_auth_token(self.coach.id)
        response = api_message_list(self.client, token, self.project.id)
        self.assert200(response)

        response = json.loads(response.data)
        self.assertEqual(6, response['total'])

        # From participant
        token, _ = encode_auth_token(self.participant.id)
        response = api_message_list(self.client, token, self.project.id)
        self.assert200(response)

        response = json.loads(response.data)
        self.assertEqual(5, response['total'])

    # def test_create_message_required_content(self):
    #     token, _ = encode_auth_token(self.sender.id)
    #     response = register_message(self.client, token, self.project.id, dict(content=None))
    #     self.assert400(response)
    #
    #     response = json.loads(response.data)
    #     self.assertIsNotNone(response['errors'])
    #     self.assertIsNotNone(response['errors']['content'])
    #
    # def test_create_message_public_success(self):
    #     # From sender
    #     token, _ = encode_auth_token(self.sender.id)
    #     response = register_message(self.client, token, self.project.id, dict(content='Test'))
    #     self.assertStatus(response, HTTPStatus.CREATED)
    #
    #     # From coach
    #     token, _ = encode_auth_token(self.coach.id)
    #     response = register_message(self.client, token, self.project.id, dict(content='Test'))
    #     self.assertStatus(response, HTTPStatus.CREATED)
    #
    #     # From participant
    #     token, _ = encode_auth_token(self.participant.id)
    #     response = register_message(self.client, token, self.project.id, dict(content='Test'))
    #     self.assertStatus(response, HTTPStatus.CREATED)
    #
    # def test_create_message_receiver_required_member(self):
    #     token, _ = encode_auth_token(self.sender.id)
    #     response = register_message(self.client, token, self.project.id, dict(content='Test', receiver=4))
    #     self.assert400(response)
    #
    #     response = json.loads(response.data)
    #     self.assertIsNotNone(response['errors'])
    #     self.assertEqual("A receiver must be a project's member.", response['errors']['receiver'])
    #
    # def test_create_message_private_required_sender_or_coach(self):
    #     # From sender
    #     token, _ = encode_auth_token(self.sender.id)
    #     response = register_message(self.client, token, self.project.id, dict(content='Test', receiver=self.coach.id))
    #     self.assertStatus(response, HTTPStatus.CREATED)
    #
    #     # From coach
    #     token, _ = encode_auth_token(self.coach.id)
    #     response = register_message(self.client, token, self.project.id, dict(content='Test', receiver=self.coach.id))
    #     self.assertStatus(response, HTTPStatus.CREATED)
    #
    #     # From participant
    #     token, _ = encode_auth_token(self.participant.id)
    #     response = register_message(self.client, token, self.project.id, dict(content='Test', receiver=self.coach.id))
    #     self.assert400(response)
    #
    #     response = json.loads(response.data)
    #     self.assertIsNotNone(response['errors'])
    #     self.assertEqual("A sender must be a project's sender or coach.", response['errors']['sender'])


if __name__ == '__main__':
    unittest.main()
