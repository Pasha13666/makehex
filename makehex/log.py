import logging
import logging.handlers
import os

import time


class DebugLogRecord:
    def __init__(self, name, _, pathname, __, msg, args, exc_info, ___=None, sinfo=None, **____):
        ct = time.time()

        fn, result, args, kwargs, extra_args = args

        self.pathname = fn.__code__.co_filename
        try:
            self.filename = os.path.basename(self.pathname)
            self.module = os.path.splitext(self.filename)[0]
        except (TypeError, ValueError, AttributeError):
            self.filename = pathname
            self.module = "Unknown module"

        self.lineno = fn.__code__.co_firstlineno
        self.funcName = ((msg + ".") if msg else "") + fn.__name__
        self.name = name
        self.msg = ("[%s] %s %s" % (result, args, kwargs)).replace("\n", "\\n")
        self.args = extra_args
        self.levelname = "D_POINT "
        self.levelno = 1
        self.exc_info = exc_info
        self.exc_text = None      # used to cache the traceback text
        self.stack_info = sinfo
        self.created = ct
        self.msecs = (ct - int(ct)) * 1000
        self.relativeCreated = (self.created - logging._startTime) * 1000
        self.thread = None
        self.threadName = None
        self.processName = None
        self.process = None

    def getMessage(self):
        msg = str(self.msg)
        if self.args:
            msg = msg % self.args
        return msg
