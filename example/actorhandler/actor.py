"""Actor handler example -- actor module

Define actor and config message for the consumer
"""

import logging

from msgvan.actors import SubscriptionActor

from thespian.actors import requireCapability


log = logging.getLogger(__name__)


class WriterSettingMessage:
    """A simple message to configure actors with an output file"""

    def __init__(self, outfile):
        self.outfile = outfile


@requireCapability("writer")
class WritingActor(SubscriptionActor):
    """An actor who can receive messages from the msgvan and writes them to file

    Needs to be configured with an output filename
    """

    fd = None

    def receiveMsg_WriterSettingMessage(self, msg, _sender):
        """On receiving a WriterSettingMessage open the outfile"""
        self.fd = open(msg.outfile, "a")
        log.debug("Got writer setting {}".format(msg))

    def receiveMsg_MessageWrapper(self, wrapper, _sender):
        """Receive a message from the van

        On receiving a message from the msgvan
        print the payload to the outfile
        """
        log.debug("Got message wrapper {}".format(wrapper))
        if self.fd is None:
            return  # No output stream yet
        print(wrapper.msg.payload, file=self.fd, flush=True)
        log.debug("Printed to {}".format(self.fd))
