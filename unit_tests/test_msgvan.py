from unittest import TestCase

from msgvan import msgvan, thespmessages


class TestMessageVan(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        msgvan.ACTORSYS = "simpleSystemBase"
        cls.van = van = msgvan.van(name="test", leader=True)
        cls.actor_sys = van.actor_sys
        cls.subscriber = cls.actor_sys.createActor("msgvan.actors.SubscriptionActor")
        van.subscribe_actor("testsubscriber", cls.subscriber, "test")
        cls.msg = msgvan.Message(payload="foo", topic="test")

    def test_publish(self):
        receiver = []
        self.actor_sys.tell(
            self.subscriber,
            thespmessages.HandlerMessage(lambda m: receiver.append(m)),
        )
        self.van.publish(self.msg)
        self.assertEqual(len(receiver), 1)
        msg = receiver[0]
        self.assertEqual(msg.payload, "foo")

    def test_subscribe_handler(self):
        test_receiver = []
        all_receiver = []
        self.van.subscribe_handler(
            "testhandler", lambda m: test_receiver.append(m), "test"
        )
        self.van.subscribe_handler("teststar", lambda m: all_receiver.append(m), ".*")
        self.van.publish(self.msg)
        other_msg = msgvan.Message(payload="bar", topic="other")
        self.van.publish(other_msg)
        self.assertEqual(len(test_receiver), 1)
        msg = test_receiver[0]
        self.assertEqual(msg.payload, "foo")
        self.assertEqual(len(all_receiver), 2)
        msg, other = all_receiver
        self.assertEqual(msg.payload, "foo")
        self.assertEqual(other.payload, "bar")

    def test_unsubscribe(self):
        receiver = []
        self.actor_sys.tell(
            self.subscriber,
            thespmessages.HandlerMessage(lambda m: receiver.append(m)),
        )
        self.van.unsubscribe("testsubscriber")
        self.van.publish(self.msg)
        self.assertFalse(receiver)
