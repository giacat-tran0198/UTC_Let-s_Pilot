"""Flask CLI/Application entry point."""

import os
import unittest
from random import choices, choice, randint

import click
from dotenv import load_dotenv

from src.chat import create_app, db, sio, redis
from src.chat.model import user, token_blacklist, project, message, push_subscription
from src.chat.service.user_service import transfer_subscription_to_redis

load_dotenv()  # take environment variables from .env.

app = create_app(os.getenv('APP_ENV') or 'development')


@app.shell_context_processor
def shell():
    return {
        'db': db,
        'User': user.User,
        'BlacklistedToken': token_blacklist.BlacklistedToken,
        'Project': project.Project,
        'Message': message.Message,
        'PushSubscription': push_subscription.PushSubscription,
        'redis': redis
    }


@app.cli.command('test')
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    return 0 if result.wasSuccessful() else 1


@app.cli.command('seed')
@click.option('--n', type=int, default=25)
def seed(n):
    """Fake data."""
    from faker import Faker
    from src.chat import db
    fake = Faker('fr-FR')

    # Remove all older data
    db.session.remove()
    db.drop_all()

    # Create database
    db.create_all()
    db.session.commit()

    # Fake data
    Faker.seed(n * 2 + 10)

    # fake for user
    list_fake_user = {'owner': [], 'coach': [], 'participant': []}
    for _ in range(n):
        fake_user = user.User(
            email=fake.unique.email(),
            username=fake.unique.domain_word(),
            password='123456',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )
        db.session.add(fake_user)

        random_value = choice(['owner', 'coach', 'participant'])
        list_fake_user[random_value].append(fake_user)

    db.session.commit()

    # fake for project
    for _ in range(n * 2):
        fake_project = project.Project(
            title=fake.unique.name(),
            owner=choice(list_fake_user['owner']),
        )
        db.session.add(fake_project)

        for user_coach in choices(list_fake_user['coach'], k=randint(1, len(list_fake_user['coach']))):
            fake_project.coaches.append(user_coach)
        for user_participant in choices(list_fake_user['participant'],
                                        k=randint(2, len(list_fake_user['participant']))):
            fake_project.participants.append(user_participant)

        db.session.commit()

        coach_id = [coach.id for coach in fake_project.coaches] + [fake_project.owner_id]
        participant_id = [participant.id for participant in fake_project.participants]
        members = coach_id + participant_id
        for _ in range(randint(1, n * 2)):
            fake_message = message.Message(
                content=fake.sentence(),
                sender_id=choice(members),
                project_id=fake_project.id,
            )
            if choices([True, False], [0.1, 0.9]) and fake_message.sender_id in coach_id:
                fake_message.receiver_id = choice(members)
            db.session.add(fake_message)

            db.session.commit()


@app.before_first_request
def first_run():
    # Remove all key before run
    keys = redis.keys()
    if keys:
        redis.delete(*keys)
    # Admin default
    if not user.User.query.filter_by(username='admin').first():
        admin = user.User(
            email='admin@admin.com',
            username='admin',
            password='admin',
            first_name='admin',
            last_name='admin',
            admin=True
        )
        db.session.add(admin)
        db.session.commit()

    transfer_subscription_to_redis()


if __name__ == '__main__':
    sio.run(app,
            port=5000,
            host='0.0.0.0',
            ssl_context=(app.config['SSL_CERTIFICATE_KEY'], app.config['SSL_PRIVATE_KEY']))
