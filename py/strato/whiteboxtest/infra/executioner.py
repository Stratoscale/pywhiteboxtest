import os
import signal
import time
import sys
import logging

from strato_common.log import discardinglogger
from strato.whiteboxtest.infra import suite
from strato.whiteboxtest.infra import timeoutthread


class Executioner:
    DEFAULT_ABORT_TEST_TIMEOUT = 10 * 60
    DEFAULT_DISCARD_LOGGING_OF = (
        'paramiko',
        'selenium.webdriver.remote.remote_connection',
        'requests.packages.urllib3.connectionpool')
    DEFAULT_SETUP_SEQUENCE = ('',)

    def __init__(self, klass):
        self._test = klass()
        self._timeoutInterval = getattr(self._test, 'ABORT_TEST_TIMEOUT', self.DEFAULT_ABORT_TEST_TIMEOUT)
        self._discardLoggingOf = getattr(self._test, 'DISCARD_LOGGING_OF', self.DEFAULT_DISCARD_LOGGING_OF)
        self._setUpSequence = getattr(self._test, 'SETUP_SEQUENCE', self.DEFAULT_SETUP_SEQUENCE)

    def executeTestScenario(self):
        timeoutthread.TimeoutThread(self._timeoutInterval, self._testTimedOut)
        logging.info(
            "Test timer armed. Timeout in %(seconds)d seconds", dict(seconds=self._timeoutInterval))
        self._setUp()
        try:
            self._run()
        finally:
            self._tearDown()
        logging.success(
            "Test completed successfully, in '%(filename)s', with %(asserts)d successfull asserts",
            dict(filename=self._filename(), asserts=suite.successfulTSAssertCount()))
        print ".:1: Test passed"

    def _testTimedOut(self):
        logging.error(
            "Timeout: test is running for more than %(seconds)ds, aborting. You might need to increase "
            "the scenario ABORT_TEST_TIMEOUT", dict(seconds=self._timeoutInterval))
        timeoutthread.TimeoutThread(10, self._killSelf)
        timeoutthread.TimeoutThread(15, self._killSelfHard)
        self._killSelf()
        time.sleep(2)
        self._killSelfHard()

    def _killSelf(self):
        os.kill(os.getpid(), signal.SIGTERM)

    def _killSelfHard(self):
        os.kill(os.getpid(), signal.SIGKILL)

    def _filename(self):
        filename = sys.modules[self._test.__class__.__module__].__file__
        if filename.endswith(".pyc"):
            filename = filename[: -1]
        return filename

    def _setUp(self):
        logging.info("Setting up test in '%(filename)s'", dict(filename=self._filename()))
        discardinglogger.discardLogsOf(self._discardLoggingOf)
        setUpStarted = []
        try:
            for identifier in self._setUpSequence:
                setUpStarted.append(identifier)
                callback = getattr(self._test, 'setUp' + identifier, None)
                if callback is None:
                    continue
                callback()
        except:
            logging.exception(
                "Failed setUp%(identifier)s method of test in '%(filename)s'",
                dict(filename=self._filename(), identifier=identifier))
            suite.outputExceptionStackTrace()
            self._tearDownNoThrow(setUpStarted)
            raise

    def _run(self):
        logging.progress("Running test in '%(filename)s'", dict(filename=self._filename()))
        assert hasattr(self._test, 'run'), "Test class must have a 'run' method"
        try:
            self._test.run()
            logging.progress(
                "Run completed successfully, in '%(filename)s', with %(asserts)d successfull asserts",
                dict(filename=self._filename(), asserts=suite.successfulTSAssertCount()))
        except:
            logging.exception("Test failed, in '%(filename)s'", dict(filename=self._filename()))
            suite.outputExceptionStackTrace()
            raise

    def _tearDown(self):
        logging.info("Tearing down test in '%(filename)s'", dict(filename=self._filename()))
        left = list(self._setUpSequence)
        try:
            while len(left) > 0:
                identifier = left.pop()
                callback = getattr(self._test, 'tearDown' + identifier, None)
                if callback is None:
                    continue
                callback()
        except:
            logging.exception(
                "Failed tearing down test in '%(filename)s'", dict(filename=self._filename()))
            suite.outputExceptionStackTrace()
            self._tearDownNoThrow(left)
            raise

    def _tearDownNoThrow(self, setUpsToTearDown):
        for identifier in reversed(setUpsToTearDown):
            callback = getattr(self._test, 'tearDown' + identifier, None)
            if callback is None:
                continue
            try:
                callback()
            except:
                logging.exception(
                    "Failed tearDown%(identifier)s method of test in '%(filename)s'",
                    dict(filename=self._filename(), identifier=identifier))
