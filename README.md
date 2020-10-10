# README

Msgvan is an embeddable messagebus library with publish-subscribe semantics for Python.

It emphasizes simplicity and correctness over performance. It's only a thin layer on top of the Thespian actor library, which handles all the heavy concurrency and distribution lifting. 

I've built msgvan because I need a pubsub library that's easily embedded in Python, but still crosses process and system boundaries, and plays well with Thespianpy. 

## Topics

All messages have a topic -- a free-format string. Processes can subscribe to a topic regex pattern. All matching messages will get delivered to that subscribing process. 

## Messages

Messages are wrapped in a message class. Besides payloads messages have a topic attribute.

Messages will be delivered to the consumers who are subscribed to a matching topic at the time the message is published. If delivery fails it will be retried.

## Subscribing processes

Subscribing processes can subscribe handler functions for message topics, or a handler object. One important caveat of the handler function is that it will be executed in the context of the Thespian process it is registered too. This may or may not be suitable for your use case.

For finer grained control on execution context it's possible to subscribe a handler object. A handler object is derived from a Thespian actor, which makes it possible to declare constraints on where it should be instantiated.

## Logging

Msgvan will log to the syslog

## Examples

### Handler function example

Module `example/msg_simple_example.py` has a two-in-one producer/consumer example.

Install the msgvan module: `pip install msgvan`

First start the example as a consumer in one terminal, and note how the main process exits -- it registered the handler function with Thespian which forked itself into the background.

```
pirx ~/msgvan/example$ python3 msgvan_simple_example.py consumer
```

Then in another terminal start the producer and give it some data:

```
pirx ~/msgvan/example$ python3 msgvan_simple_example.py producer
Producer: enter a line
Hey there o/
```

Subsequently the first terminal should print out something like the following:

```
pirx ~/msgvan/example$ Handler got  Message(payload='Hey there o/', topic='exampletopic1')
```

Note this is printed from the Thespian process in the background, which
is executing the handler functions for subscribers.


### Handler actor example


Package `example/actorhandler` has an example publish/subscribe application to be run across a network. It features a message producer and consumer, where a producer creates messages for a topic, and one subscribers will receive messages for a given topic and write those to file.

For this example you need 2 machines, two VMs or containers will do fine. Install msgvan, and make the example code available in each machine. The consumer application will be considered the leader, note it's ipaddress, for example `10.0.8.1`. The consumer and producer must be able to communicate on tcp port 1900 (the default Thespian port).

Start a consumer application on one machine, pass in a topic to subscribe to and a path where to write messages:

```
vm-1 ~/example$ python3 actorhandler/consumer.py --ipaddr 10.0.8.1 --topic foo --outfile /tmp/consumer.out     
```

Start a producer application on another machine, creating a message for a topic:

```
vm-2 ~/example$ python3 actorhandler/producer.py --ipaddr 10.0.8.1 --topic foo bar 
```

On the consumer machine, the consumer outfile should now hold the sent message:

```
vm-1 ~/example$ cat /tmp/consumer.out
bar
```

#### Caveats

This example requires (at least) two distinct machines,  virtual or physical. This is because it assumes a separate leader and non-leader Thespian node.

Be aware that on each machine a Thespian admin process will be launched on first run of producer and consumer. It will fork itself and stay alive in the background, even when the producer/consumer process itself has shutdown. Actors have the same lifetime as the Thespian process, so to make code changes you need to ensure that those Thespian processes are killed, otherwise your changes will never be loaded.


## Thespian

Msgvan is built on top of the Thespian actor library for Python.

- Home page: https://thespianpy.com/doc
- Code on Github: https://github.com/kquick/Thespian
- Intro blog post on Thespian: https://sabaini.at/peterlog/posts/2020/Feb/16/thespian-a-python-actor-system/
- The excellent user group: https://groups.google.com/forum/#!forum/thespianpy

