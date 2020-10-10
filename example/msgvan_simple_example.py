"""Example of a msgvan producer/consumer

- Consumer subscribes a handler function to an exampletopic

- Producer reads stdin and publishes each line to exampletopic

"""
import sys

import msgvan
from msgvan import Message


def handler_func(msg):
    """Handler function, will receive published messsages"""
    print("Handler got ", msg)


if __name__ == "__main__":
    # msgvan.van() creates an entry point for subscribing and publishing
    van = msgvan.van(leader=True)
    role = sys.argv[1]

    if role == "producer":
        # If started as producer, read line from stdin, wrap it in a
        # Message object and publish
        print("Producer: enter a line")
        for line in sys.stdin:
            msg = Message(payload=line.strip(), topic="exampletopic1")
            van.publish(msg)
    elif role == "consumer":
        # If started as consumer, subscribe a handler function to
        # to any topic starting with example
        van.subscribe_handler("handlertst", handler_func, "example.*")
        # The main process will exit here, and the handler function
        # will be executed inside the Thespian admin process
