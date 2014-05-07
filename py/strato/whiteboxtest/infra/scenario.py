import logging
from strato.whiteboxtest.infra import suite
from strato.whiteboxtest.infra import timeoutthread
from strato.common.log import discardinglogger
import os
import signal
import time
import sys


class Scenario:
    ABORT_TEST_TIMEOUT = 10 * 60
    DISCARD_LOGGING_OF = (
        'paramiko',
        'selenium.webdriver.remote.remote_connection',
        'requests.packages.urllib3.connectionpool')

    def setUp(self):
        logging.info("No set up phase defined")

    def tearDown(self):
        logging.info("No tear down phase defined")

    def run(self):
        assert False, "You must implement a 'run' method"

    def executeTestScenario(self):
        timeoutthread.TimeoutThread(self.ABORT_TEST_TIMEOUT, self.__testTimedOut)
        logging.info(
            "Test timer armed. Timeout in %(seconds)d seconds", dict(seconds=self.ABORT_TEST_TIMEOUT))
        self.__setUp()
        try:
            self.__run()
        finally:
            self.__tearDown()

    def __testTimedOut(self):
        logging.error(
            "Timeout: test is running for more than %(seconds)ds, aborting. You might need to increase "
            "the scenario ABORT_TEST_TIMEOUT", dict(seconds=self.ABORT_TEST_TIMEOUT))
        timeoutthread.TimeoutThread(10, self.__killSelf)
        timeoutthread.TimeoutThread(15, self.__killSelfHard)
        self.__killSelf()
        time.sleep(2)
        self.__killSelfHard()

    def __killSelf(self):
        os.kill(os.getpid(), signal.SIGTERM)

    def __killSelfHard(self):
        os.kill(os.getpid(), signal.SIGKILL)

    def __filename(self):
        filename = sys.modules[self.__class__.__module__].__file__
        if filename.endswith(".pyc"):
            filename = filename[: -1]
        return filename

    def __setUp(self):
        logging.info("Setting up test in '%(filename)s'", dict(filename=self.__filename()))
        discardinglogger.discardLogsOf(self.DISCARD_LOGGING_OF)
        try:
            self.setUp()
        except:
            logging.exception(
                "Failed setting up test in '%(filename)s'", dict(filename=self.__filename()))
            suite.outputExceptionStackTrace()
            raise

    def __run(self):
        logging.progress("Running test in '%(filename)s'", dict(filename=self.__filename()))
        try:
            self.run()
            logging.success(
                "Test completed successfully, in '%(filename)s', with %(asserts)d successfull asserts",
                dict(filename=self.__filename(), asserts=suite.successfulTSAssertCount()))
            print ".:1: Test passed"
        except:
            logging.exception("Test failed, in '%(filename)s'", dict(filename=self.__filename()))
            suite.outputExceptionStackTrace()
            raise

    def __tearDown(self):
        logging.info("Tearing down test in '%(filename)s'", dict(filename=self.__filename()))
        try:
            self.tearDown()
        except:
            logging.exception(
                "Failed tearing down test in '%(filename)s'", dict(filename=self.__filename()))
            suite.outputExceptionStackTrace()
            raise
