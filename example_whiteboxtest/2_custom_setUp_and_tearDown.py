from strato.whiteboxtest.infra.suite import *
import atexit


class Test:
    SETUP_SEQUENCE = ('First', 'Second', 'Third')
    called = []

    def setUp(self):
        assert False, " '' is not in the SETUP_SEQUENCE, this should not be called"

    def setUpFirst(self):
        TS_ASSERT_EQUALS(self.called, [])
        self.called.append("setUpFirst")

    # no setUpSecond

    def setUpThird(self):
        TS_ASSERT_EQUALS(self.called, ['setUpFirst'])
        self.called.append("setUpThird")

    def run(self):
        TS_ASSERT_EQUALS(self.called, ['setUpFirst', 'setUpThird'])
        self.called.append("run")

    def tearDown(self):
        assert False, " '' is not in the SETUP_SEQUENCE, this should not be called"

    def tearDownSecond(self):
        TS_ASSERT_EQUALS(self.called, ['setUpFirst', 'setUpThird', 'run'])
        self.called.append("tearDownSecond")

    def tearDownFirst(self):
        TS_ASSERT_EQUALS(self.called, ['setUpFirst', 'setUpThird', 'run', 'tearDownSecond'])
        global failOnExit
        failOnExit = False


def _dieAtExit():
    global failOnExit
    if not failOnExit:
        return
    raise Exception("SETUP_SEQUENCE feature verification failed")


failOnExit = True
atexit.register(_dieAtExit)
