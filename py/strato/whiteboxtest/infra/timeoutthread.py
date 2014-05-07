import time
import threading


class TimeoutThread(threading.Thread):
    def __init__(self, interval, callback):
        self._interval = interval
        self._callback = callback
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def safeRun(self):
        time.sleep(self._interval)
        self._callback()
