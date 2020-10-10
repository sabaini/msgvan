"""Actor handler example producer

The producer reads lines from stdin and publishes them as messages for
the given topic
"""
import argparse
import logging

import msgvan

log = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", level=logging.DEBUG)


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--ipaddr")
    argp.add_argument("--topic", default="default")
    argp.add_argument("message")
    args = argp.parse_args()
    van = msgvan.van(addr=args.ipaddr, verbose=True)
    msg = msgvan.Message(payload=args.message.strip(), topic=args.topic.strip())
    log.debug("Producer: publishing %s to van %s", msg, van)
    van.publish(msg)


if __name__ == "__main__":
    main()
