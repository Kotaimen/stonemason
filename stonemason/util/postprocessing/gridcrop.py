# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/5/15'

""" Shelve buffer from a rendered map Tile, or crop a rendered MetaTile into Tiles.
Pillow is required for image IO and image processing.
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

    Shave buffer pixels from given tile image, returns a
    `PIL.Image.Image` object. If `buffer_size` is zero, the image
    is returned without modification.

    The given `image` can be one of:

    - PIL/Pillow Image
    - `bytes` contains a image file data
    - File handle of a image file

    Note the image must be square.

    Due to PIL/Pillow Image internal lazy cropping implement, the
    `image` object's internal buffer must remain unchanged until
    cropped image is serialized.
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
    """ Crop a image into grids

    Crop a large image into a `stride x stride` image grid, shave
    extra buffer pixels during the process  (aka: `MetaTile` fission).

    The given `image` can be one of:

    - PIL/Pillow Image
    - `bytes` contains a image file data
    - File handle of a image file

    Returns a `dict` of small grid images::

        (row, column): Image.Image object

    Note the image must be square.

    Due to PIL/Pillow Image internal lazy cropping implement, the
    `image` object's internal buffer must remain unchanged until
    cropped image is serialized.
    """

    assert stride >= 1

    if stride == 1:
        return {(0, 0): shave(image, buffer_size=buffer_size)}

    image = open_image(image)

    width, height = image.size
    assert width == height
    assert buffer_size < width / 2
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

