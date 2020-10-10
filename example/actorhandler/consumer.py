"""Actor handler example consumer

The consumer subscribes to a topic and writes received messages
to file via a WritingActor
"""

import argparse
import logging

from actorhandler.actor import WriterSettingMessage

import msgvan


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", level=logging.DEBUG)


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--ipaddr")
    argp.add_argument("--unsubscribe", action="store_true")
    argp.add_argument("--topic", default="default")
    argp.add_argument("--outfile", default="/tmp/consumer.out")
    args = argp.parse_args()
    # Create a msg van, give it writer capabilities, and make it the leader
    van = msgvan.van(
        addr=args.ipaddr, capabilities={"writer": True}, leader=True, verbose=True
    )
    # We are unsubscribing
    if args.unsubscribe:
        van.unsubscribe("write_actor")
        log.debug("Unsubscribed write_actor")
        return
    # Fall through: subscribe an actor
    # Create an actor which will receive messages
    write_actor = van.actor_sys.createActor("actorhandler.actor.WritingActor")
    # Configure the writer actor with a WriterSettingMessage
    van.actor_sys.tell(write_actor, WriterSettingMessage(args.outfile))
    # Finally subscribe the actor to the given topic
    van.subscribe_actor("write_actor", write_actor, args.topic)
    log.debug("Consumer: van %s, writer %s, topic %s", van, write_actor, args.topic)


if __name__ == "__main__":
    main()
