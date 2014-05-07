from strato.whiteboxtest.infra.suite import *
from strato.whiteboxtest.infra import scenario

class Test(scenario.Scenario):
    def run(self):
        TS_FAIL("Failing on purpose")
