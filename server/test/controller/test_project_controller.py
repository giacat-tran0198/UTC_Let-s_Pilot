import json
import unittest
from http import HTTPStatus
from typing import Dict

from flask import url_for

from src.chat import db
from src.chat.model.project import Project
from src.chat.model.user import User
from src.chat.service.auth_service import encode_auth_token
from test.base import BaseTestCase


def register_project(client, token: str, data: Dict):
    return client.post(
        url_for('api.project_v1_list'),
        data=json.dumps(data),
        headers=dict(Authorization='Bearer ' + token),
        content_type='application/json'
    )


def api_project_list(client, token: str):
    return client.get(
        url_for('api.project_v1_list'),
        headers=dict(Authorization='Bearer ' + token),
        content_type='application/json'
    )


def api_project_item(func, id: int, token: str, data: Dict = None):
    return func(
        url_for('api.project_v1_item', id=id),
        data=json.dumps(data),
        headers=dict(Authorization='Bearer ' + token),
        content_type='application/json'
    )


def api_invite_into_project(client, id: int, token: str, data: Dict):
    return client.post(
        url_for('api.project_v1_invite', id=id),
        data=json.dumps(data),
        headers=dict(Authorization='Bearer ' + token),
        content_type='application/json'
    )


def api_leave_into_project(client, id: int, token: str):
    return client.delete(
        url_for('api.project_v1_leave', id=id),
        headers=dict(Authorization='Bearer ' + token),
        content_type='application/json'
    )


def api_designate_in_project(func, id: int, token: str, data: Dict):
    return func(
        url_for('api.project_v1_designate', id=id),
        data=json.dumps(data),
        headers=dict(Authorization='Bearer ' + token),
        content_type='application/json'
    )


def api_kick_out_from_project(client, id: int, token: str, data: Dict):
    return client.delete(
        url_for('api.project_v1_kick_out', id=id),
        data=json.dumps(data),
        headers=dict(Authorization='Bearer ' + token),
        content_type='application/json'
    )


class TestProjectController(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.seed()

    def seed(self):
        # Owner
        self.owner = User(
            email='owner@test.com',
            password='test',
            username='username',
            first_name='first name',
            last_name='last name',
        )
        db.session.add(self.owner)

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

        # Other user
        self.user = User(
            email='user@test.com',
            password='test',
            username='user',
            first_name='first name',
            last_name='last name',
        )

        db.session.add(self.user)

        # Project
        self.project = Project(
            title='project0',
            owner=self.owner
        )
        db.session.add(self.project)

        self.project.coaches.append(self.coach)
        self.project.participants.append(self.participant)

        db.session.commit()

    def test_create_project_required_title(self):
        data = dict()
        token, _ = encode_auth_token(self.owner.id)

        response = register_project(self.client, token, data)

        self.assert400(response)

        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['title'])

    def test_create_existed_project_receive_conflict(self):
        data = dict(title=self.project.title)
        token, _ = encode_auth_token(self.owner.id)

        response = register_project(self.client, token, data)

        self.assertStatus(response, HTTPStatus.CONFLICT)

    def test_create_project_success_without_coaches_and_participants(self):
        data = dict(title=self.project.title + ' success')
        token, _ = encode_auth_token(self.owner.id)

        response = register_project(self.client, token, data)

        self.assertStatus(response, HTTPStatus.CREATED)

        response = json.loads(response.data)

        self.assertEqual(self.project.title + ' success', response['title'])
        self.assertEqual(self.owner.id, response['owner']['id'])
        self.assertEqual([], response['coaches'])
        self.assertEqual([], response['participants'])

    def test_create_project_success_with_only_coaches(self):
        data = dict(
            title=self.project.title + ' success',
            coaches=[self.coach.id]
        )
        token, _ = encode_auth_token(self.owner.id)

        response = register_project(self.client, token, data)

        self.assertStatus(response, HTTPStatus.CREATED)

        response = json.loads(response.data)

        self.assertEqual(self.project.title + ' success', response['title'])
        self.assertEqual(self.owner.id, response['owner']['id'])
        self.assertTrue(any(self.coach.id == user['id'] for user in response['coaches']))
        self.assertEqual([], response['participants'])

    def test_create_project_success_with_only_participants(self):
        data = dict(
            title=self.project.title + ' success',
            participants=[self.participant.id]
        )
        token, _ = encode_auth_token(self.owner.id)

        response = register_project(self.client, token, data)

        self.assertStatus(response, HTTPStatus.CREATED)

        response = json.loads(response.data)

        self.assertEqual(self.project.title + ' success', response['title'])
        self.assertEqual(self.owner.id, response['owner']['id'])
        self.assertEqual([], response['coaches'])
        self.assertTrue(any(self.participant.id == user['id'] for user in response['participants']))

    def test_create_project_success_with_one_participant_in_list_coaches_will_be_coache(self):
        data = dict(
            title=self.project.title + ' success',
            coaches=[self.participant.id],
            participants=[self.participant.id],
        )
        token, _ = encode_auth_token(self.owner.id)

        response = register_project(self.client, token, data)

        self.assertStatus(response, HTTPStatus.CREATED)

        response = json.loads(response.data)

        self.assertEqual(self.project.title + ' success', response['title'])
        self.assertEqual(self.owner.id, response['owner']['id'])
        self.assertEqual(1, len(response['coaches']))
        self.assertTrue(any(self.participant.id == user['id'] for user in response['coaches']))
        self.assertEqual([], response['participants'])

    def test_get_list_project_of_owner_success(self):
        token, _ = encode_auth_token(self.owner.id)

        response = api_project_list(self.client, token)

        self.assert200(response)

        response = json.loads(response.data)

        self.assertEqual(1, response['total'])
        self.assertEqual(self.project.title, response['data'][0]['title'])
        self.assertEqual(self.owner.id, response['data'][0]['owner']['id'])

    def test_get_list_project_of_coach_success(self):
        token, _ = encode_auth_token(self.coach.id)

        response = api_project_list(self.client, token)

        self.assert200(response)

        response = json.loads(response.data)

        self.assertEqual(1, response['total'])
        self.assertEqual(self.project.title, response['data'][0]['title'])
        self.assertTrue(any(self.coach.id == user['id'] for user in response['data'][0]['coaches']))

    def test_get_list_project_of_participant_success(self):
        token, _ = encode_auth_token(self.participant.id)

        response = api_project_list(self.client, token)

        self.assert200(response)

        response = json.loads(response.data)

        self.assertEqual(1, response['total'])
        self.assertEqual(self.project.title, response['data'][0]['title'])
        self.assertTrue(any(self.participant.id == user['id'] for user in response['data'][0]['participants']))

    def test_edit_project_only_owner(self):
        # Owner
        token, _ = encode_auth_token(self.owner.id)
        response = api_project_item(
            func=self.client.put,
            id=self.project.id,
            token=token,
            data=dict(title='edit'))
        self.assert200(response)

        # Not owner
        token, _ = encode_auth_token(self.coach.id)
        response = api_project_item(
            func=self.client.put,
            id=self.project.id,
            token=token,
            data=dict(title='edit'))
        self.assert403(response)

    def test_delete_project_only_owner(self):
        # Not owner
        token, _ = encode_auth_token(self.coach.id)
        response = api_project_item(
            func=self.client.delete,
            id=self.project.id,
            token=token)
        self.assert403(response)

        # Owner
        token, _ = encode_auth_token(self.owner.id)
        response = api_project_item(
            func=self.client.delete,
            id=self.project.id,
            token=token)
        self.assert200(response)

    def test_not_member_invite_person_into_project_receive_forbidden(self):
        token, _ = encode_auth_token(self.user.id)
        response = api_invite_into_project(
            client=self.client,
            id=self.project.id,
            token=token,
            data=dict(participant=self.user.id)
        )
        self.assert403(response)

    def test_invite_require_person_into_project_receive_errors(self):
        token, _ = encode_auth_token(self.participant.id)
        response = api_invite_into_project(
            client=self.client,
            id=self.project.id,
            token=token,
            data=dict(participant=None)
        )
        self.assert400(response)

        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['participant'])

    def test_invite_existing_project_person_into_project_receive_errors(self):
        token, _ = encode_auth_token(self.participant.id)
        response = api_invite_into_project(
            client=self.client,
            id=self.project.id,
            token=token,
            data=dict(participant=self.owner.id)
        )
        self.assert400(response)

        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['participant'])
        self.assertEqual("You can't add an existing project member.", response['errors']['participant'])

    def test_invite_person_into_project_success(self):
        token, _ = encode_auth_token(self.participant.id)
        response = api_invite_into_project(
            client=self.client,
            id=self.project.id,
            token=token,
            data=dict(participant=self.user.id)
        )
        self.assert200(response)

    def test_not_member_leave_project_receive_forbidden(self):
        token, _ = encode_auth_token(self.user.id)
        response = api_leave_into_project(
            client=self.client,
            id=self.project.id,
            token=token,
        )
        self.assert403(response)

    def test_owner_can_not_leave_project_receive_badrequest(self):
        token, _ = encode_auth_token(self.owner.id)
        response = api_leave_into_project(
            client=self.client,
            id=self.project.id,
            token=token,
        )
        self.assert400(response)

        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['owner'])
        self.assertEqual("The owner can't leave the project.", response['errors']['owner'])

    def test_member_leave_project_receive_Ok(self):
        token, _ = encode_auth_token(self.coach.id)
        response = api_leave_into_project(
            client=self.client,
            id=self.project.id,
            token=token,
        )
        self.assert200(response)

    def test_only_coach_and_owner_designate_receive_forbidden(self):
        token, _ = encode_auth_token(self.participant.id)
        response = api_designate_in_project(
            func=self.client.post,
            data=dict(coach=self.participant.id),
            id=self.project.id,
            token=token,
        )
        self.assert403(response)

    def test_coach_and_owner_designate_not_member_become_coach_recive_badrequest(self):
        token, _ = encode_auth_token(self.coach.id)
        response = api_designate_in_project(
            func=self.client.post,
            data=dict(coach=self.user.id),
            id=self.project.id,
            token=token,
        )
        self.assert400(response)
        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['coach'])
        self.assertEqual("You can't add a not member become a new coach.", response['errors']['coach'])

    def test_coach_and_owner_designate_member_become_coach_recive_Ok(self):
        token, _ = encode_auth_token(self.coach.id)
        response = api_designate_in_project(
            func=self.client.post,
            data=dict(coach=self.participant.id),
            id=self.project.id,
            token=token,
        )
        self.assert200(response)
        self.assertFalse(self.participant in self.project.participants)

    def test_only_coach_and_owner_withdraw_receive_forbidden(self):
        token, _ = encode_auth_token(self.participant.id)
        response = api_designate_in_project(
            func=self.client.delete,
            data=dict(coach=self.coach.id),
            id=self.project.id,
            token=token,
        )
        self.assert403(response)

    def test_coach_and_owner_withdraw_owner_become_participant_recive_badrequest(self):
        token, _ = encode_auth_token(self.coach.id)
        response = api_designate_in_project(
            func=self.client.delete,
            data=dict(coach=self.owner.id),
            id=self.project.id,
            token=token,
        )
        self.assert400(response)
        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['coach'])
        self.assertEqual("You can't withdraw a not coach become a participant.", response['errors']['coach'])

    def test_coach_and_owner_withdraw_participant_become_participant_recive_badrequest(self):
        token, _ = encode_auth_token(self.coach.id)
        response = api_designate_in_project(
            func=self.client.delete,
            data=dict(coach=self.participant.id),
            id=self.project.id,
            token=token,
        )
        self.assert400(response)
        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['coach'])
        self.assertEqual("You can't withdraw a not coach become a participant.", response['errors']['coach'])

    def test_coach_and_owner_withdraw_coach_become_coach_recive_Ok(self):
        token, _ = encode_auth_token(self.coach.id)
        response = api_designate_in_project(
            func=self.client.delete,
            data=dict(coach=self.coach.id),
            id=self.project.id,
            token=token,
        )
        self.assert200(response)
        self.assertFalse(self.coach in self.project.coaches)

    def test_only_coach_and_owner_remove_participant_receive_forbidden(self):
        token, _ = encode_auth_token(self.participant.id)
        response = api_kick_out_from_project(
            client=self.client,
            data=dict(participant=self.coach.id),
            id=self.project.id,
            token=token,
        )
        self.assert403(response)

    def test_coach_and_owner_remove_owner_or_coach_from_project_recive_badrequest(self):
        # remove owner
        token, _ = encode_auth_token(self.coach.id)
        response = api_kick_out_from_project(
            client=self.client,
            data=dict(participant=self.owner.id),
            id=self.project.id,
            token=token,
        )

        self.assert400(response)
        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['participant'])
        self.assertEqual("You can't remove an owner or coach from project.", response['errors']['participant'])

        # remove coach
        token, _ = encode_auth_token(self.coach.id)
        response = api_kick_out_from_project(
            client=self.client,
            data=dict(participant=self.coach.id),
            id=self.project.id,
            token=token,
        )
        self.assert400(response)
        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['participant'])
        self.assertEqual("You can't remove an owner or coach from project.", response['errors']['participant'])

    def test_coach_and_owner_remove_not_member_recive_badrequest(self):
        token, _ = encode_auth_token(self.coach.id)
        response = api_kick_out_from_project(
            client=self.client,
            data=dict(participant=self.user.id),
            id=self.project.id,
            token=token,
        )
        self.assert400(response)
        response = json.loads(response.data)

        self.assertIsNotNone(response['errors'])
        self.assertIsNotNone(response['errors']['participant'])
        self.assertEqual("You can't remove a not member from project.", response['errors']['participant'])

    def test_coach_and_owner_participant_recive_Ok(self):
        token, _ = encode_auth_token(self.coach.id)
        response = api_kick_out_from_project(
            client=self.client,
            data=dict(participant=self.participant.id),
            id=self.project.id,
            token=token,
        )
        self.assert200(response)
        self.assertFalse(self.participant in self.project.participants)


if __name__ == '__main__':
    unittest.main()
