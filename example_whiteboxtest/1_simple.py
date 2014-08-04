from strato.whiteboxtest.infra.suite import *
import atexit

class Test:
    def setUp(self):
        self.setUpCalled = True
        self.tearDownCalled = False
        self.failOnExit = True
        atexit.register(self._dieAtExit)

    def tearDown(self):
        self.failOnExit = False

    def run(self):
        TS_ASSERT_EQUALS(1 + 1, 2)
        TS_ASSERT(self.setUpCalled)
        TS_ASSERT(not self.tearDownCalled)

    def _dieAtExit(self):
        if not self.failOnExit:
            return
        raise Exception("tearDown was not called")
