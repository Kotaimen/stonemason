# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/4/15'

import unittest
import time
import io
import re

from stonemason.util.timer import Timer, human_duration


class TestTimer(unittest.TestCase):
    def test_human_duration(self):
        self.assertEqual(human_duration(0.00123), '1.23ms')
        self.assertEqual(human_duration(1.23), '1.2300s')
        self.assertEqual(human_duration(123), '2.05m')
        self.assertEqual(human_duration(12345), '3h25.75m')

    def test_timer_message(self):
        timer = Timer(message='Time: %(time)s')
        timer.tic()
        time.sleep(1)
        timer.tac()

        message = timer.get_message()

        self.assertIsNotNone(re.match(r'Time: [01]\.\d+s', message))
        self.assertLess(abs(timer.get_time() - 1), 0.5)

    def test_timer_with(self):
        class Writer(object):
            def __init__(self):
                self.message = ''

            def __call__(self, message):
                self.message += message

        writer = Writer()

        with Timer(writer=writer):
            time.sleep(1)

        self.assertIsNotNone(
            re.match(r'Time taken: [01]\.\d+s', writer.message))


if __name__ == '__main__':
    unittest.main()
