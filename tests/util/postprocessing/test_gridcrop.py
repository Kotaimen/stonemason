# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/5/15'

import unittest
import os
import io
from distutils.version import StrictVersion
import six
import PIL
from PIL import Image
import stonemason.util.postprocessing.gridcrop as gridcrop
from tests import DATA_DIRECTORY, TEST_DIRECTORY, ImageTestCase


class TestGridCrop(ImageTestCase):
    def setUp(self):
        grid_image = os.path.join(DATA_DIRECTORY, 'grid_crop',
                                  'grid.png')
        self.grid_data = open(grid_image, mode='rb').read()
        self.grid_file = open(grid_image, mode='rb')
        self.grid_image = Image.open(grid_image)

    def test_version(self):
        try:
            # Any reasonably recent Pillow is fine
            self.assertGreaterEqual(StrictVersion(PIL.PILLOW_VERSION),
                                    StrictVersion('2.0.0'))
        except AttributeError:
            # PIL version must be 1.1.7
            self.assertEqual(StrictVersion(PIL.VERSION),
                             StrictVersion('1.1.7'))

    def test_shave(self):
        self.assertEqual(self.grid_image.size, (1024, 1024))
        expected_cropped_image = self.grid_image.crop((256, 256, 768, 768))

        self.assertImageEqual(expected_cropped_image,
                              gridcrop.shave(self.grid_image, 256))

        self.assertImageEqual(expected_cropped_image,
                              gridcrop.shave(self.grid_file, 256))

        self.assertImageEqual(expected_cropped_image,
                              gridcrop.shave(self.grid_data, 256))

        self.assertImageNotEqual(expected_cropped_image,
                                 gridcrop.shave(self.grid_data, 0))

        self.assertImageEqual(expected_cropped_image,
                              list(gridcrop.grid_crop(self.grid_data, stride=1,
                                                      buffer_size=256))[0][1])

    def test_grid_crop(self):
        grids = dict(gridcrop.grid_crop(self.grid_data, stride=2,
                                        buffer_size=256))
        # visual confirm
        output_dir = os.path.join(TEST_DIRECTORY, 'grid_crop')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for (row, column), image in six.iteritems(grids):
            filename = os.path.join(output_dir, '%d-%d.png' % (row, column))
            image.save(filename)

        self.assertImageEqual(grids[(0, 0)],
                              self.grid_image.crop((256, 256, 512, 512)))

        self.assertImageEqual(grids[(0, 1)],
                              self.grid_image.crop((256, 512, 512, 768)))

        self.assertImageEqual(grids[(1, 0)],
                              self.grid_image.crop((512, 256, 768, 512)))

    def test_grid_crop_into_data(self):

        grids = dict(gridcrop.grid_crop_into_data(self.grid_data,
                                                  stride=2,
                                                  buffer_size=256,
                                                  format='PNG',
                                                  ))

        self.assertImageEqual(Image.open(io.BytesIO(grids[(0, 0)])),
                              self.grid_image.crop((256, 256, 512, 512)))

    def test_grid_crop_into_data2(self):

        grids = dict(gridcrop.grid_crop_into_data(self.grid_data,
                                                  stride=2,
                                                  buffer_size=256,
                                                  format='PNG',
                                                  parameters=dict(convert='P',
                                                                  colors=4,
                                                                  palette=1)
                                                  ))

        self.assertImageEqual(Image.open(io.BytesIO(grids[(0, 0)])),
                              self.grid_image.crop(
                                  (256, 256, 512, 512)).convert('RGB').convert(
                                  'P',
                                  colors=4,
                                  palette=1)
                              )


if __name__ == '__main__':
    unittest.main()
