import logging
import sys
import unittest
from pathlib import Path
from subprocess import check_output

from retrying import retry

import zaza.model as model


BASE = Path(__file__).parent
EXAMPLE = BASE / "../example"
MSGVAN = BASE / "../src"
PEX = BASE / "../dist/example.pex"
REQS = ["thespian", "attrs"]


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
log = logging.getLogger("testlogger")


def build_example():
    check_output(["pex", "-o", str(PEX), "-D", str(MSGVAN), "-D", str(EXAMPLE)] + REQS)


class BaseMsgvanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up tests."""
        super().setUpClass()
        cls.model_name = model.get_juju_model()
        build_example()
        for app in "leader", "follower":
            model.scp_to_all_units(app, PEX, "/tmp")

    @staticmethod
    def run_cmd(ip, topic, mod, msg="", outfile=None, unsubscribe=False):
        if outfile:
            # consumer subscribe
            extra = " --outfile {}".format(outfile)
        elif unsubscribe:
            extra = " --unsubscribe"
        else:
            # producer
            extra = msg
        cmd = """function bg {{
                  /tmp/example.pex -m {} --ipaddr {} --topic '{}' {}
                }}
                export THESPLOG_THRESHOLD=DEBUG
                bg < /dev/null >> /tmp/test.out 2>&1 &
                disown
                """.format(
            mod, ip, topic, extra
        )
        return cmd

    @staticmethod
    def run_producer(topic, msg):
        ip = model.get_lead_unit_ip("leader")
        cmd = BaseMsgvanTest.run_cmd(ip, topic, "actorhandler.producer", msg=msg)
        model.run_on_unit("leader/0", cmd)
        log.info("Running producer, ip %s", ip)

    @staticmethod
    def run_consumer(topic, outfile=None, unsubscribe=None):
        ip = model.get_lead_unit_ip("leader")
        cmd = BaseMsgvanTest.run_cmd(
            ip,
            topic,
            "actorhandler.consumer",
            outfile=outfile,
            unsubscribe=unsubscribe,
        )
        model.run_on_unit("follower/0", cmd)
        log.info("Running consumer, ip %s", ip)

    @staticmethod
    def cat_unit(unit, path):
        unit_res = model.run_on_unit(unit, "sudo cat {}".format(path))
        return unit_res["Stdout"]

    def run_test(self, producer_topic, consumer_topic, message, outfile):
        model.run_on_unit("follower/0", "rm {}".format(outfile))
        self.run_consumer(consumer_topic, outfile=outfile)
        self.run_producer(producer_topic, message)

        @retry(
            stop_max_attempt_number=3,
            wait_fixed=1000,
            retry_on_result=lambda d: d != message,
        )
        def tst():
            out = self.cat_unit("follower/0", outfile)
            log.info("Get consumer output: %s", out)
            return out.strip()

        return tst() == message


class MsgvanTest(BaseMsgvanTest):
    """Basic msgvan operation"""

    def test_10_no_subscribers(self):
        self.run_producer("default", "no-subscriber")

    def test_15_star_subscriber(self):
        self.assertTrue(
            self.run_test("testtopic", ".*", "star_message", "/tmp/star.out")
        )

    def test_20_specific_subscriber(self):
        self.assertTrue(
            self.run_test(
                "testtopic",
                "testtopic",
                "specific_message",
                "/tmp/specific.out",
            )
        )

    def test_25_unsubscribe(self):
        self.run_consumer("testtopic", unsubscribe=True)
        self.run_producer("testtopic", "unsubscribed")
        out = self.cat_unit("follower/0", "/tmp/specific.out")
        self.assertTrue("unsubcribed" not in out)
