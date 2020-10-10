"""The actors module
"""
import collections
import logging
import re

from msgvan.util import flatten

from thespian.actors import ActorTypeDispatcher, requireCapability


log = logging.getLogger(__name__)


@requireCapability("msgvan-leader")
class MessageVanActor(ActorTypeDispatcher):
    """Handles subscriptions and message publication"""

    def __init__(self):
        self.subscription_topics = collections.defaultdict(dict)
        super().__init__()

    def receiveMsg_AddSubMessage(self, sub, _sender):  # noqa N802
        """Store a subscription"""
        self.subscription_topics[re.compile(sub.topic)][sub.name] = sub.actor
        log.debug("Van actor got sub %s, have now: %s", sub, self.subscription_topics)

    def _find_subs(self, topic):
        subs = [
            subdict.values()
            for pat, subdict in self.subscription_topics.items()
            if pat.match(topic)
        ]
        return flatten(subs)

    def receiveMsg_MessageWrapper(self, wrapper, _sender):
        """Receive a message and publish to subscribers"""
        subs = list(self._find_subs(wrapper.msg.topic))
        log.debug(
            "Van actor got wrapper %s for subs %s, topic: %s, all subs: %s",
            wrapper,
            (subs),
            wrapper.msg.topic,
            self.subscription_topics,
        )
        for sub in subs:
            log.debug("Sending msg %s to sub %s", wrapper, sub)
            self.send(sub, wrapper)

    def receiveMsg_DelSubMessage(self, sub, _sender):
        """Remove a subscription"""
        log.debug("Van actor got unsubscribe", sub.name)
        for subdict in self.subscription_topics.values():
            try:
                del subdict[sub.name]
            except KeyError:
                pass
        log.debug("Van actor subscriptions", self.subscription_topics)

    def receiveMsg_StatusRequest(self, _req, sender):
        self.send(sender, self.subscription_topics)


class SubscriptionActor(ActorTypeDispatcher):
    """An actor class for subscriptions.

    This is dual-use: it can be subclassed for subscription actors, but is
    also used directly to handle function subscriptions
    """

    def receiveMsg_HandlerMessage(self, msg, sender):
        self.handler = msg.handler_func

    def receiveMsg_MessageWrapper(self, wrapper, _sender):
        self.handler(wrapper.msg)
