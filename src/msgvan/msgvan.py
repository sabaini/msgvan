"""The msgvan module

Has a factory function for message vans and a base class for messages to be sent
"""
import logging
import logging.handlers

import attr

from msgvan.thespmessages import (
    AddSubMessage,
    DelSubMessage,
    HandlerMessage,
    MessageWrapper,
    StatusRequest,
)

from thespian.actors import ActorSystem


ACTORSYS = "multiprocTCPBase"
log = logging.getLogger(__name__)
log.addHandler(logging.handlers.SysLogHandler(address="/dev/log"))
logcfg = {"version": 1, "loggers": {__name__: {"level": logging.WARNING}}}


def van(name="default", addr=None, capabilities=None, leader=False, verbose=False):
    """Construct a message van
    :param name: van name
    :param addr: ipaddr:port where we want to connect to, defaults to local
    :param capabilities: additional capabilities
    :param leader: Make this msgvan system the leader
    :return: MessageVan object
    """
    if leader:
        caps = {"msgvan-leader": leader}
    else:
        caps = {}
    if addr is not None:
        caps["Convention Address.IPv4"] = (addr, 1900)
    if capabilities is not None:
        caps.update(capabilities)
    if verbose:
        logcfg["loggers"][__name__]["level"] = logging.DEBUG
        log.setLevel(logging.DEBUG)
    asys = ActorSystem(ACTORSYS, capabilities=caps, logDefs=logcfg)
    van = MessageVan(name, asys)
    log.debug("Started van %s, actor sys %s, caps %s", van, asys, caps)
    return van


class MessageVan:
    """MessageVan: entry point for message vans

    Creates a thespian actorsys, and a MessageVanActor

    Handles subscriptions and receives messages for publication
    """

    def __init__(self, name, actor_sys):
        self.name = name
        self.actor_sys = actor_sys
        self.van_actor = actor_sys.createActor(
            "msgvan.actors.MessageVanActor",
            globalName="msgvan-{}".format(name),
        )

    def publish(self, msg):
        """Publish a message
        :param msg:
        :return: None
        """
        log.debug("Publish %s", msg)
        self.actor_sys.tell(self.van_actor, MessageWrapper(msg))

    def subscribe_handler(self, name, handler, topic_pat):
        """Subscribe a function to topic
        :param handler: A handler function which will receive matching messages
        :param topic_pat: regexp topic pattern
        :return: a subscription identifier (actor address)
        """
        log.debug("Subscribe handler to %s", topic_pat)
        act = self.actor_sys.createActor("msgvan.actors.SubscriptionActor")
        self.actor_sys.tell(act, HandlerMessage(handler))
        self.subscribe_actor(name, act, topic_pat)

    def subscribe_actor(self, name, actor, topic_pat):
        """Subscribe an actor to topic
        :param actor: Thespian actor
        :param topic_pat: regexp pattern
        :return: None
        """
        log.debug("Subscribe actor %s to %s", actor, topic_pat)
        self.actor_sys.tell(self.van_actor, AddSubMessage(name, topic_pat, actor))

    def unsubscribe(self, name):
        """Unsubscribe the named actor or function"""
        log.debug("Unsubscribe %s", name)
        self.actor_sys.tell(self.van_actor, DelSubMessage(name))

    def status(self):
        """Return the subscribers registered"""
        log.debug("Statusrequest")
        return self.actor_sys.ask(self.van_actor, StatusRequest())


@attr.s
class Message:
    """Message to be published

    Consists of a payload and a topic
    """

    payload = attr.ib()

    topic = attr.ib(factory=set)
