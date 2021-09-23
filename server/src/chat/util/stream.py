"""Logic for """

import json
from collections import OrderedDict

from flask import stream_with_context, Response, current_app
from pywebpush import webpush, WebPushException
from redis.client import PubSub

from src.chat import redis


class Message(object):
    """
    Data that is published as a server-sent event.
    """

    def __init__(self, data, type=None, id=None, retry=30000):
        """
        Create a server-sent event.
        :param data: The event data. If it is not a string, it will be
            serialized to JSON using the Flask application's
            :class:`~flask.json.JSONEncoder`.
        :param type: An optional event type.
        :param id: An optional event ID.
        :param retry: An optional integer, to specify the reconnect time for
            disconnected clients of this stream. Default: after 30s
        """
        self.data = data
        self.type = type
        self.id = id
        self.retry = retry

    def to_dict(self):
        """
        Serialize this object to a minimal dictionary, for storing in Redis.
        """
        # data is required, all others are optional
        d = {"data": self.data}
        if self.type:
            d["type"] = self.type
        if self.id:
            d["id"] = self.id
        if self.retry:
            d["retry"] = self.retry
        return d

    def __str__(self):
        """
        Serialize this object to a string, according to the `server-sent events specification`.
        """
        data = json.dumps(self.data)
        lines = ["data:{value}".format(value=line) for line in data.splitlines()]
        if self.type:
            lines.insert(0, "event:{value}".format(value=self.type))
        if self.id:
            lines.append("id:{value}".format(value=self.id))
        if self.retry:
            lines.append("retry:{value}".format(value=self.retry))
        return "\n".join(lines) + "\n\n"

    def __repr__(self):
        kwargs = OrderedDict()
        if self.type:
            kwargs["type"] = self.type
        if self.id:
            kwargs["id"] = self.id
        if self.retry:
            kwargs["retry"] = self.retry
        kwargs_repr = "".join(
            ", {key}={value!r}".format(key=key, value=value)
            for key, value in kwargs.items()
        )
        return "{classname}({data!r}{kwargs})".format(
            classname=self.__class__.__name__,
            data=self.data,
            kwargs=kwargs_repr,
        )

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__) and
                self.data == other.data and
                self.type == other.type and
                self.id == other.id and
                self.retry == other.retry
        )


def publish(channel: str, data, type: str = None, id: int = None, retry: int = 30000) -> None:
    """
    Publish data as a server-sent event or as a webpush.

    :param channel: If you want to direct different events to different
        clients, you may specify a channel for this event to go to.
        Only clients listening to the same channel will receive this event.
    :param data: The event data. If it is not a string, it will be
        serialized to JSON using the Flask application's.
    :param type: An optional event type.
    :param id: An optional event ID. (Only SSE)
    :param retry: An optional integer, to specify the reconnect time for
        disconnected clients of this stream. Default: after 30s (Only SSE)
    """
    # If channel exist, we will send notification
    sse_val = redis.get(sub_sse(channel))
    webpush_val = redis.get(sub_webpush(channel))

    if sse_val:
        message = Message(data, type=type, id=id, retry=retry)
        msg_json = json.dumps(message.to_dict())
        redis.publish(sse_val, msg_json)
    elif webpush_val:
        trigger_push_notifications_for_subscriptions(webpush_val, data, type)


def messages(channel: str = 'sse'):
    """
        A generator objects from the given channel.
    """
    pubsub = redis.pubsub()
    pubsub.subscribe(channel)

    # Mark existence channel
    redis.set(channel, channel)

    try:
        for pubsub_message in pubsub.listen():
            if pubsub_message['type'] == 'message':
                msg_dict = json.loads(pubsub_message['data'])
                yield Message(**msg_dict)
    finally:
        try:
            disconnect_sse(channel, pubsub)

        except ConnectionError as e:
            current_app.logger.error(str(e), exc_info=True)


def disconnect_sse(channel: str = 'sse', pubsub: PubSub = None, user_id: int = None) -> None:
    """A function will remove all older data SSE"""

    # Create new channel follow user's id
    if user_id:
        channel = sub_sse(sub_user_channel(user_id))

    # unsubscribe older channel
    if pubsub:
        pubsub.unsubscribe(channel)

    # Delete older channel
    redis.delete(channel)


def stream(user_id: int) -> Response:
    """
    A view function that streams server-sent events.
    :param user_id: The user's id for event SSE.
    :return: The context's stream with 'event-stream' mimetype
    """
    channel_sse = sub_sse(sub_user_channel(user_id))

    @stream_with_context
    def generator():
        for message in messages(channel=channel_sse):
            yield str(message)

    return Response(
        generator(),
        mimetype='text/event-stream',
    )


def trigger_push_notifications_for_subscriptions(webpush_val, data, type: str = None) -> None:
    """
    The function to send the notification to the subscriber.
    :param webpush_val: The public key's client is format string or bytes.
    :param data: The event data.
    :param type: An optional event type.
    """
    try:
        if isinstance(webpush_val, bytes):
            webpush_val = webpush_val.decode('utf-8')
        webpush(
            subscription_info=json.loads(webpush_val),
            data=json.dumps(dict(type=type, data=data)),
            vapid_private_key=current_app.config['VAPID_PRIVATE_KEY'],
            vapid_claims=current_app.config['VAPID_CLAIMS']
        )
    except WebPushException as e:
        current_app.logger.error(str(e), exc_info=True)


def sub_sse(channel: str) -> str:
    """Convert channel into the SSE channel."""
    if 'webpush:' in channel:
        raise Exception("'webpush' is not in the sse channel.")
    if 'sse:' in channel:
        return channel
    return f'sse:{channel}'


def sub_webpush(channel: str) -> str:
    """Convert channel into the Webpush channel."""
    if 'sse:' in channel:
        raise Exception("'sse' is not in the webpush channel.")
    if 'webpush:' in channel:
        return channel
    return f'webpush:{channel}'


def sub_user_channel(user_id: int) -> str:
    """Create channel for subscribe."""

    return f"sub:user:{user_id}"
