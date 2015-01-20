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
    """Crop a big MetaTile image into a image grid.

    Crop a large image into a `stride*stride` image grid, shave
    extra buffer pixels during the process  (aka: MetaTile *fission*).

    Given image can be one of:

    - A PIL/Pillow image
    - `bytes` contains a image file data
    - `file` handle of a image file (real file or `io.BytesIO`)

    Returns a iterator of small grid images:

        `(row, column), image`

    Due to PIL/Pillow Image internal lazy cropping implement, given
    `image` object's internal buffer must remain unchanged until
    cropped image is serialized.

    :param image: Image to crop, must be square.
    :type image: :class:`PIL.Image.Image` or `bytes` or `file`
    :param stride: Number of grid images per axis.
    :param buffer_size: Size of the buffer to be shaved each side in pixels,
                        default is 0, means no buffer is shaved.
    :return: A iterator of cropped image.
    :rtype: iterator
    """

    assert stride >= 1

    if stride == 1:
        yield (0, 0), shave(image, buffer_size=buffer_size)
        return

    image = open_image(image)

    width, height = image.size
    assert width == height
    assert buffer_size < width / 2
    width -= buffer_size * 2
    height -= buffer_size * 2
    rows, columns = stride, stride
    grid_width = grid_height = width // stride

    for row in range(0, rows):
        for column in range(0, columns):
            left = row * grid_width + buffer_size
            top = column * grid_height + buffer_size
            right = left + grid_width
            bottom = top + grid_height

            crop_box = (left, top, right, bottom)
            grid = image.crop(crop_box)
            yield (row, column), grid


def grid_crop_into_data(image, stride=1, buffer_size=0,
                        format=None, parameters=None):
    """Crop MetaTile image into a grid and written as image files.

    Same as :func:`grid_crop` except returns image file data instead of
    :class:`PIL.Image.Image`.

    `format`
        Image format supported by PIL/Pillow, eg: ``JPEG``, ``PNG``, ``WEBP``.
        The actual list for formats depends on Pillow installation, see
        `image formats`_ for a complete format list.

    `parameters`
        Image saving parameters, available list depends on `format` selected.
        `image formats`_ for a complete parameter list.

    Some examples:

        format='JPEG'
        parameters={'optimize'=True, 'quality'=80}

    .. _image formats: <https://pillow.readthedocs.org/handbook/image-file-formats.html>

    See :func:`~stonemason.util.postprocessing.gridrop` for parameter descriptions.

    .. note::
        Pillow won't do convert colorspaces when saving images, so convert
        `image` to P mode first if a paletted image is required.

    :param image: Image to crop, must be square.
    :type image: :class:`PIL.Image.Image` or `bytes` or `file`
    :param stride: Number of grid images per axis.
    :param buffer_size: Size of the buffer to be shaved each side in pixels,
                        default is 0, means no buffer is shaved.
    :param format: Image format, default means same as given image.
    :param parameters: Image save parameters as a dictionary.
    :return: A iterator of cropped image data.
    :rtype: iterator
    """

    image = open_image(image)

    # inherit image format if its not given
    if format is None:
        format = image.format

    if parameters is None:
        parameters = {}

    for (row, column), grid_image in grid_crop(image, stride, buffer_size):
        buf = io.BytesIO()
        grid_image.save(buf, format=format, **parameters)
        grid_data = buf.getvalue()
        del buf
        yield (row, column), grid_data