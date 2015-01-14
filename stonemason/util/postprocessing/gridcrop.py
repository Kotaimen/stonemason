# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/5/15'

"""
    stonemason.util.postprocessing.gridrop
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Shelve buffer from a rendered map Tile, or crop a rendered MetaTile
    into Tiles.

    PIL/Pillow is required for image IO and image processing.

"""

import io

import six
from PIL import Image


def open_image(image):
    if isinstance(image, Image.Image):
        # Already a PIL/Pillow image
        return image
    elif isinstance(image, six.binary_type):
        # Bytes
        return Image.open(io.BytesIO(image))
    else:
        # Open a file object
        return Image.open(image)


def shave(image, buffer_size=0):
    """ Shave buffer pixel from given image.

    Shave buffer pixels from the given tile image, returns a
    :class:`PIL.Image.Image` object. If `buffer_size` is zero, given image
    is returned without modification.

    Given image can be one of:

    - PIL/Pillow image
    - `bytes` contains a image file data
    - `fp` of a image file (real file or :class:`io.BytesIO`)

    Due to PIL/Pillow Image internal lazy cropping implement, given
    `image` object's internal buffer must remain unchanged until
    cropped image is serialized.

    :param image: Image to crop, must be square.
    :type image: :class:`PIL.Image.Image` or `bytes` or `file`
    :param buffer_size: Size of the buffer to be shaved each side in pixels,
                        default is ``0``, which means no buffer is shaved.
    :return: Cropped image.
    :rtype: :class:`PIL.Image.Image`
    """
    assert buffer_size >= 0
    image = open_image(image)

    if buffer_size == 0:
        return image

    width, height = image.size
    assert width == height
    assert buffer_size < width / 2

    crop_box = [buffer_size, buffer_size,
                width - buffer_size,
                height - buffer_size]

    return image.crop(crop_box)


def grid_crop(image, stride=1, buffer_size=0):
    """ Crop a big MetaTile image into a image grid.

    Crop a large image into a `stride*stride` image grid, shave
    extra buffer pixels during the process  (aka: MetaTile *fission*).

    Given image can be one of:

    - A PIL/Pillow image
    - `bytes` contains a image file data
    - `file` handle of a image file (real file or `io.BytesIO`)

    Returns a dictionary of small grid images: `(row, column): image`

    Due to PIL/Pillow Image internal lazy cropping implement, given
    `image` object's internal buffer must remain unchanged until
    cropped image is serialized.

    :param image: Image to crop, must be square.
    :type image: :class:`PIL.Image.Image` or `bytes` or `file`
    :param stride: Number of grid images per axis.
    :param buffer_size: Size of the buffer to be shaved each side in pixels,
                        default is 0, means no buffer is shaved.
    :return: A dictionary of cropped image.
    :rtype: dict
    """

    assert stride >= 1

    if stride == 1:
        return {(0, 0): shave(image, buffer_size=buffer_size)}

    image = open_image(image)

    width, height = image.size
    assert width == height
    assert buffer_size < width / 2
    width -= buffer_size * 2
    height -= buffer_size * 2
    rows, columns = stride, stride
    grid_width = grid_height = width // stride

    grids = dict()
    for row in range(0, rows):
        for column in range(0, columns):
            left = row * grid_width + buffer_size
            top = column * grid_height + buffer_size
            right = left + grid_width
            bottom = top + grid_height

            crop_box = (left, top, right, bottom)
            grid = image.crop(crop_box)
            grids[(row, column)] = grid

    return grids

