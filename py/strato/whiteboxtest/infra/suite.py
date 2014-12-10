import time
import logging
import pprint
import traceback
import sys


class TestFailureException(Exception):
    pass

_successful_TS_ASSERT_Count = 0
_interactOnAssert = False


def enableInteractOnAssert():
    global _interactOnAssert
    _interactOnAssert = True


def successfulTSAssertCount():
    global _successful_TS_ASSERT_Count
    return _successful_TS_ASSERT_Count


def outputExceptionStackTrace():
    exceptionType, exception, traceBack = sys.exc_info()
    stack = list(reversed(traceback.extract_tb(traceBack)))
    filename, line = stack[0][: 2]
    result = "%s:%d: Exception %s\n" % (filename, line, exception)
    if len(stack) > 1:
        result += "STACK TRACE:\n"
        for filename, line, function, text in stack[1:]:
            result += "%s:%d: from Here: %s\n" % (filename, line, text)
        result += "STACK TRACE END\n"
    print result


def formatException(skip=1):
    exception_list = traceback.format_stack()
    exception_list = exception_list[: -skip]
    exception_str = "Assertion traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[: -1]
    return exception_str


def raiseAssert(msg, exc_type=TestFailureException):
    if _interactOnAssert:
        e_locals = {}
        try:
            raise exc_type(msg)
        except:
            e_locals = sys.exc_info()[2].tb_frame.f_back.f_back.f_locals
            print formatException(skip=3)
            outputExceptionStackTrace()
        print "Local variables: %r" % (e_locals.keys(),)
        print "Invoking interactive shell: (skip_assert=1 causes the exception to be ignored)"
        from code import interact
        interact(local=e_locals)
        if 'skip_assert' in e_locals:
            return
    raise exc_type(msg)


def TS_FAIL(message):
    raiseAssert(message)


def TS_ASSERT_PREDICATE_TIMEOUT(predicate, * args, ** kwargs):
    global _successful_TS_ASSERT_Count
    if 'TS_timeout' in kwargs:
        timeout = kwargs['TS_timeout']
        del kwargs['TS_timeout']
    else:
        timeout = 3
    if 'TS_interval' in kwargs:
        interval = kwargs['TS_interval']
        del kwargs['TS_interval']
    else:
        interval = 0.25
    before = time.time()
    while time.time() - before < timeout:
        try:
            if predicate(* args, ** kwargs):
                _successful_TS_ASSERT_Count += 1
                return
            else:
                time.sleep(interval)
        except:
            time.sleep(interval)
    if predicate(* args, ** kwargs):
        _successful_TS_ASSERT_Count += 1
        return
    else:
        raiseAssert("TS_ASSERT_PREDICATE_TIMEOUT failed: %s" % predicate)


def TS_ASSERT(value, message='TS_ASSERT failed'):
    if not value:
        raiseAssert(message)
    global _successful_TS_ASSERT_Count
    _successful_TS_ASSERT_Count += 1


def TS_ASSERT_LESS_THAN(valueA, valueB):
    if not (valueA < valueB):
        raiseAssert("TS_ASSERT_LESS_THAN failed: '%s' >= '%s'" % (valueA, valueB))
    global _successful_TS_ASSERT_Count
    _successful_TS_ASSERT_Count += 1


def TS_ASSERT_LESS_THAN_EQUALS(valueA, valueB):
    if not (valueA <= valueB):
        raiseAssert("TS_ASSERT_LESS_THAN_EQUALS failed: '%s' > '%s'" % (valueA, valueB))
    global _successful_TS_ASSERT_Count
    _successful_TS_ASSERT_Count += 1


def TS_ASSERT_IN(valueA, valueB):
    if not (valueA in valueB):
        raiseAssert(
            "TS_ASSERT_IN failed: '%s' not in '%s'" % (pprint.pformat(valueA), pprint.pformat(valueB)))
    global _successful_TS_ASSERT_Count
    _successful_TS_ASSERT_Count += 1


def TS_ASSERT_NOT_IN(valueA, valueB):
    if valueA in valueB:
        raiseAssert(
            "TS_ASSERT_NOT_IN failed: '%s' is in '%s'" % (pprint.pformat(valueA), pprint.pformat(valueB)))
    global _successful_TS_ASSERT_Count
    _successful_TS_ASSERT_Count += 1


def TS_ASSERT_EQUALS(valueA, valueB):
    if not (valueA == valueB):
        raiseAssert(
            "TS_ASSERT_EQUALS failed: '%s' != '%s'" % (pprint.pformat(valueA), pprint.pformat(valueB)))
    global _successful_TS_ASSERT_Count
    _successful_TS_ASSERT_Count += 1


def TS_ASSERT_DIFFERS(valueA, valueB):
    if not (valueA != valueB):
        raiseAssert(
            "TS_ASSERT_DIFFERS failed: '%s' == '%s'" % (pprint.pformat(valueA), pprint.pformat(valueB)))
    global _successful_TS_ASSERT_Count
    _successful_TS_ASSERT_Count += 1


def TS_ASSERT_THROWS_ANYTHING(call, * args, ** kwargs):
    try:
        call(* args, ** kwargs)
    except:
        global _successful_TS_ASSERT_Count
        _successful_TS_ASSERT_Count += 1
    else:
        raiseAssert("TS_ASSERT_THROWS_ANYTHING failed")


def TS_ASSERT_THROWS(exceptionClass, call, * args, ** kwargs):
    try:
        call(* args, ** kwargs)
    except exceptionClass:
        global _successful_TS_ASSERT_Count
        _successful_TS_ASSERT_Count += 1
    else:
        raiseAssert("TS_ASSERT_THROWS failed: no exception thrown")


def sleep(interval, reason):
    logging.progress(
        "Sleeping for %(interval).3f, Reason: '%(reason)s'",
        dict(interval=interval, reason=reason))
    time.sleep(interval)
    logging.progress(
        "Done sleeping for %(interval).3f, Reason: '%(reason)s'",
        dict(interval=interval, reason=reason))
