import unittest

from src.chat.service.project_service import *
from test.base import BaseTestCase


class TestProjectService(BaseTestCase):
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

    def test_insert_coaches(self):
        insert_coaches(id_project=self.project.id, coaches=[self.user.id])

        self.assertIn(self.user, self.project.coaches)

    def test_insert_participants(self):
        insert_participants(id_project=self.project.id, participants=[self.user.id])

        self.assertIn(self.user, self.project.participants)

    def test_required_owner_in_project(self):
        # It's owner
        self.assertIsNone(required_own_project(
            user_id=self.owner.id,
            project=self.project
        ))

        # It's not owner
        self.assertRaises(Forbidden,
                          required_own_project,
                          self.coach.id, self.project)

    def test_required_owner_or_coach_in_project(self):
        # It's owner
        self.assertIsNone(required_own_or_coach_in_project(
            user_id=self.owner.id,
            project=self.project
        ))

        # It's not owner
        self.assertRaises(Forbidden,
                          required_own_or_coach_in_project,
                          self.user.id, self.project)

        # It's coach
        self.assertIsNone(required_own_or_coach_in_project(
            user_id=self.coach.id,
            project=self.project
        ))

        # It's not coach
        self.assertRaises(Forbidden,
                          required_own_or_coach_in_project,
                          self.user.id, self.project)

    def test_required_member_in_project(self):
        # It's owner
        self.assertIsNone(required_member_in_project(
            user_id=self.owner.id,
            project=self.project
        ))

        # It's not owner
        self.assertRaises(Forbidden,
                          required_member_in_project,
                          self.user.id, self.project)

        # It's coach
        self.assertIsNone(required_member_in_project(
            user_id=self.coach.id,
            project=self.project
        ))

        # It's not coach
        self.assertRaises(Forbidden,
                          required_member_in_project,
                          self.user.id, self.project)

        # It's participant
        self.assertIsNone(required_member_in_project(
            user_id=self.participant.id,
            project=self.project
        ))

        # It's not coach
        self.assertRaises(Forbidden,
                          required_member_in_project,
                          self.user.id, self.project)


if __name__ == '__main__':
    unittest.main()
