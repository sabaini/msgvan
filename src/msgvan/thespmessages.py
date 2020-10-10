"""Thespian messages
"""
import attr


@attr.s
class AddSubMessage:

    name = attr.ib()

    topic = attr.ib()

    actor = attr.ib()


@attr.s
class DelSubMessage:

    name = attr.ib()


class StatusRequest:
    pass


@attr.s
class HandlerMessage:
    """Wrap a handler function for a subscriber"""

    handler_func = attr.ib()


@attr.s
class MessageWrapper:
    """Wrap a message"""

    msg = attr.ib()
