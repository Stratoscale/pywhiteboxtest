import unittest
import subprocess
import shutil
import json


class Test(unittest.TestCase):
    def setUp(self):
        shutil.rmtree('logs.whiteboxtest', ignore_errors=True)

    def test_firstExample(self):
        subprocess.check_output(
            './runner --scenariosRoot=example_whiteboxtest',
            shell=True, close_fds=True, stderr=subprocess.STDOUT)
        with open('logs.whiteboxtest/whiteboxtestrunnerreport.json') as f:
            report = json.load(f)
        self.assertEquals(len(report), 2)
        self.assertEquals(report[0]['scenario'], 'example_whiteboxtest/1_simple.py')
        self.assertTrue(report[0]['passed'])
        self.assertEquals(report[1]['scenario'], 'example_whiteboxtest/2_custom_setUp_and_tearDown.py')
        self.assertTrue(report[1]['passed'])

    def test_failingExample(self):
        try:
            subprocess.check_output(
                'python py/strato/whiteboxtest/runner/main.py '
                '--scenariosRoot=example_whiteboxtest_fails',
                shell=True, close_fds=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            pass
        else:
            raise Exception("Runner should fail if test failes")
        with open('logs.whiteboxtest/whiteboxtestrunnerreport.json') as f:
            report = json.load(f)
        self.assertEquals(len(report), 1)
        self.assertEquals(report[0]['scenario'], 'example_whiteboxtest_fails/1_fails.py')
        self.assertFalse(report[0]['passed'])

if __name__ == '__main__':
    unittest.main()
