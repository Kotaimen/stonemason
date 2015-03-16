# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/14/15'

import unittest
import re
import os
from distutils.version import LooseVersion

from tests import skipUnlessHasImageMagick, HAS_IMAGEMAGICK, \
    DATA_DIRECTORY, TEST_DIRECTORY


if HAS_IMAGEMAGICK:
    from stonemason.util.postprocessing.magickcmd import convert, version, \
        MagickError


# @skipUnlessHasImageMagick()
class TestMagickCmd(unittest.TestCase):
    def setUp(self):
        self.rose = os.path.join(TEST_DIRECTORY, 'rose.png')
        if os.path.exists(self.rose):
            os.unlink(self.rose)

    def test_version(self):
        v = version()
        m = re.search(r'^ImageMagick (\d\.\d+\.\d+)-\d+', v)
        if m:
            self.assertGreaterEqual(LooseVersion(m.group(1)),
                                    LooseVersion('6.6.9'))
        else:
            self.assert_(False, v)

    def test_convert(self):
        status = convert(['rose:', '-negate', self.rose])
        self.assertTrue(os.path.exists(self.rose))

    def test_convert_fail(self):
        self.assertRaises(MagickError,
                          convert,
                          ['rose:', '-bad-option', self.rose])

    # def test_convert_complex(self):

        # convert(['rose:', 'png:-'])

if __name__ == '__main__':
    unittest.main()
