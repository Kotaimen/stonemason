# -*- encoding: utf-8 -*-

"""
    stonemason.util.timer
    ~~~~~~~~~~~~~~~~~~~~~

    TicTac timer.
"""

__author__ = 'kotaimen'
__date__ = '5/7/12'

import sys
import time
import email


def timestamp2mtime(timestamp):
    """Convert RFC 2822 datetime string used by s3 to mtime."""
    modified = email.utils.parsedate_tz(timestamp)
    if modified is None:
        return None
    mtime = email.utils.mktime_tz(modified)
    return float(mtime)


def mtime2timestamp(mtime):
    """Convert mtime to RFC 2822 datetime string."""
    return email.utils.formatdate(mtime)


def human_duration(d):
    """ Return a formatted human readable duration.

    >>> from stonemason.util.timer import human_duration
    >>> human_duration(0.00123)
    '1.23ms'
    >>> human_duration(1.23)
    '1.2300s'
    >>> human_duration(123)
    '2.05m'
    >>> human_duration(12345)
    '3h25.75m'

    :param d: Time duration in seconds.
    :type d: float

    :return: Formatted duration.
    :rtype: str
    """
    if d > 3600:
        return '%dh%.2fm' % (d // 3600, d % 3600 / 60.)
    elif d > 60:
        return '%.2fm' % (d / 60.)
    elif d > 0.1:
        return '%.4fs' % d
    else:
        return '%.2fms' % (d * 1000.)


class Timer(object):
    """A simple tic-tac clock.

    >>> import time
    >>> from stonemason.util.timer import Timer
    >>> with Timer(writer=print): #doctest: +SKIP
    ...     time.sleep(0.01)
    Time taken: ...ms
    >>> with Timer(writer=print):  #doctest: +SKIP
    ...     time.sleep(1)
    Time taken: ...s

    :param message: Formatted message, must include ``%(time)s``, default
        value is ``'Time taken: %(time)s'``.
    :type message: str

    :param writer: A function to write message, default is ``stdout``.
    :type writer: function

    :param newline: Whether to append newline to the message, default is
        ``True``.
    :type newline: bool

    """

    def __init__(self,
                 message='Time taken: %(time)s',
                 writer=sys.stderr.write,
                 newline=True):
        self._message = message
        self._writer = writer
        self._tic = 0.
        self._tac = 0.
        self._newline = newline
        # On win32, time.clock() has higher resolution
        if sys.platform == 'win32':
            self.timer = time.clock
        else:
            self.timer = time.time

    def tic(self):
        self._tic = self.timer()

    def tac(self):
        self._tac = self.timer()

    def get_timestr(self):
        diff = self._tac - self._tic
        return human_duration(diff)

    def get_message(self):
        """ Get formatted elapsed time.

        :return: Formatted elapsed time message.
        :rtype: str
        """
        return self._message % {'time': self.get_timestr()}

    def get_time(self):
        """ Get elapsed time.

        :return: Elapsed time in seconds.
        :rtype: float
        """
        return self._tac - self._tic

    def __enter__(self):
        self.tic()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.tac()
        self._writer(self.get_message())
        if self._newline:
            self._writer('\n')
