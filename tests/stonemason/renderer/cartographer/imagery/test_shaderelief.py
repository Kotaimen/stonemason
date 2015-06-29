# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/28/15'

import os
import unittest
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from PIL import Image as im

import skimage.exposure

from tests import TEST_DIRECTORY

from stonemason.renderer.cartographer.imagery.shaderelief import *


def array2image(array):
    array = array.astype(np.float)
    image = im.fromarray(array)
    # image = image.convert('RGBA')
    return image


def array2png(array):
    array = array.astype(np.uint8)
    image = im.fromarray(array, mode='L')
    image = image.convert('RGBA')
    return image

#
# def make_test_gradient_image():
#     array = np.fromfunction(lambda i, j: j, (512, 512), dtype=np.uint8)
#     image = array2image(array)
#     image.save(os.path.join(TEST_DIRECTORY, 'gradient.png'), 'png')
#

# def contour(elevation):
#     width, height = elevation.shape
#     x = np.linspace(0, width, width)
#     y = np.linspace(0, height, height)
#     X, Y = np.meshgrid(x, y)
#
#     plt.contourf(X, Y, elevation, 8, alpha=.75, cmap='jet')
#     C = plt.contour(X, Y, elevation, 8, colors='black', linewidth=.5)
#
#     plt.clabel(C, inline=1, fontsize=10)
#
#     plt.xticks(())
#     plt.yticks(())
#     plt.show()


def mock_elevation():
    stride = 512
    center = (stride / 2 - 1, stride / 2 - 1)

    scale = 1.0

    def circle(x, y):
        z = stride / 2. - np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
        z[z < 0] = 0
        return scale * z

    elevation = np.fromfunction(circle, (stride, stride), dtype=np.float)

    # contour(elevation)

    return elevation


class TestAspectAndSlope(unittest.TestCase):
    def test_aspect_and_slope(self):
        elevation = mock_elevation()

        aspect, slope = aspect_and_slope(
            elevation, resx=1, resy=1, zfactor=1, scale=1)

        shade = hillshade(aspect, slope, 315, 45)
        shade = skimage.exposure.adjust_sigmoid(shade, cutoff=0.8, gain=2,
                                                inv=False) + 0.05

        shade = (255 * shade).astype(np.ubyte)
        image = array2png(shade)
        image.save(os.path.join(TEST_DIRECTORY, 'hillshade2.png'), 'png')
