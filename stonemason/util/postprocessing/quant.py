# -*- encoding: utf-8 -*-

"""
    stonemason.util.postprocessing.quant
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Image quantlization.


"""
__author__ = 'kotaimen'
__date__ = '11/25/15'

import io
from PIL import Image

import mapnik

def imgquant(image, colors=256):
    # assert isinstance(image, Image)
    buf = io.BytesIO()

    image.save(buf, format='PNG', compression=0, optimized=False)

    # See https://github.com/mapnik/mapnik/wiki/Image-IO
    mapnik_image = mapnik.Image.frombuffer(buf.getbuffer())
    return mapnik_image.tostring('png8:c=%d' % colors)