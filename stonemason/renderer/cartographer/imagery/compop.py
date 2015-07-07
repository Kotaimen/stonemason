# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/4/15'

import skimage
import numpy as np
from PIL import Image


def img2array(img):
    array = np.array(img)
    return array


def array2img(array, mode='RGBA'):
    im = Image.fromarray(array, mode=mode)
    return im


def img_as_float(array):
    return skimage.img_as_float(array)


def img_as_ubyte(array):
    return skimage.img_as_ubyte(array)


def test_image_1():
    width, height, channels = 256, 256, 4
    row, col = np.ogrid[:height, :width]

    mask = row + col < width

    src = np.zeros((width, height, channels), dtype=np.uint8)
    src[mask] = [255, 255, 0, 255]

    return src


def test_image_2():
    width, height, channels = 256, 256, 4
    row, col = np.ogrid[:height, :width]

    mask = col - row >= 0

    src = np.zeros((width, height, channels), dtype=np.uint8)
    src[mask] = [0, 0, 255, 255]

    return src


def test_image_3():
    width, height, channels = 256, 256, 4
    sr = sg = sb = np.fromfunction(
        lambda i, j: j, (width, height), dtype=np.uint8)
    sa = 255 * np.ones((width, height), dtype=np.uint8)
    src = np.dstack((sr, sg, sb, sa))
    return src


def test_image_4():
    width, height, channels = 256, 256, 4
    sr = sg = sb = np.fromfunction(
        lambda i, j: 255 - i, (width, height), dtype=np.uint8)
    sa = 255 * np.ones((width, height), dtype=np.uint8)
    src = np.dstack((sr, sg, sb, sa))
    return src


def premultiply(src):
    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    mask = sa == 0
    mask_not = np.logical_not(mask)

    sr[mask] = sg[mask] = sb[mask] = 0
    sr[mask_not] *= sa[mask_not]
    sg[mask_not] *= sa[mask_not]
    sb[mask_not] *= sa[mask_not]

    premultiplied = np.dstack((sr, sg, sb, sa))

    return premultiplied


def demultiply(src):
    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    mask = sa == 0
    mask_not = np.logical_not(mask)

    sr[mask] = sg[mask] = sb[mask] = 0
    sr[mask_not] /= sa[mask_not]
    sg[mask_not] /= sa[mask_not]
    sb[mask_not] /= sa[mask_not]

    demultiplied = np.dstack((sr, sg, sb, sa))

    return demultiplied


def comp_op_clear(src, dst):
    """
    Dca' = 0
    Da'  = 0
    """
    assert src.shape == dst.shape

    composite = np.zeros_like(src)
    return composite


def comp_op_src(src, dst):
    """
    Dca' = Sca × Da + Sca × (1 - Da)
         = Sca
    Da'  = Sa × Da + Sa × (1 - Da)
         = Sa
    """
    assert src.shape == dst.shape

    return src


def comp_op_dst(src, dst):
    """
    Dca' = Dca × Sa + Dca × (1 - Sa)
         = Dca
    Da'  = Da × Sa + Da × (1 - Sa)
         = Da
    """
    assert src.shape == dst.shape

    return dst


def comp_op_src_over(src, dst):
    """
    Dca' = Sca × Da + Sca × (1 - Da) + Dca × (1 - Sa)
         = Sca + Dca × (1 - Sa)
    Da'  = Sa × Da + Sa × (1 - Da) + Da × (1 - Sa)
         = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    s1a = 1. - sa

    dr = sr + dr * s1a
    dg = sg + dg * s1a
    db = sb + db * s1a
    da = sa + da * s1a

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_dst_over(src, dst):
    """
    Dca' = Dca × Sa + Sca × (1 - Da) + Dca × (1 - Sa)
         = Dca + Sca × (1 - Da)
    Da'  = Da × Sa + Sa × (1 - Da) + Da × (1 - Sa)
         = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1. - da

    dr = dr + sr * d1a
    dg = dg + sg * d1a
    db = db + sb * d1a
    da = da + sa * d1a

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_src_in(src, dst):
    """
    Dca' = Sca × Da
    Da'  = Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    dr = sr * da
    dg = sg * da
    db = sb * da
    da = sa * da

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_dst_in(src, dst):
    """
    Dca' = Dca × Sa
    Da'  = Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    dr = dr * sa
    dg = dg * sa
    db = db * sa
    da = sa * da

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_src_out(src, dst):
    """
    Dca' = Sca × (1 - Da)
    Da'  = Sa × (1 - Da)
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1 - da

    dr = sr * d1a
    dg = sg * d1a
    db = sb * d1a
    da = sa * d1a

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_dst_out(src, dst):
    """
    Dca' = Dca × (1 - Sa)
    Da'  = Da × (1 - Sa)
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    s1a = 1 - sa

    dr = dr * s1a
    dg = dg * s1a
    db = db * s1a
    da = da * s1a

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_src_atop(src, dst):
    """
    Dca' = Sca × Da + Dca × (1 - Sa)
    Da'  = Sa × Da + Da × (1 - Sa)
         = Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    s1a = 1 - sa

    dr = sr * da + dr * s1a
    dg = sg * da + dg * s1a
    db = sb * da + db * s1a
    da = da

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_dst_atop(src, dst):
    """
    Dca' = Dca × Sa + Sca × (1 - Da)
    Da'  = Da × Sa + Sa × (1 - Da)
         = Sa
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1 - da

    dr = dr * sa + sr * d1a
    dg = dg * sa + sg * d1a
    db = db * sa + sb * d1a
    da = sa

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_xor(src, dst):
    """
    Dca' = Sca × (1 - Da) + Dca × (1 - Sa)
    Da'  = Sa × (1 - Da) + Da × (1 - Sa)
         = Sa + Da - 2 × Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1 - da
    s1a = 1 - sa

    dr = sr * d1a + dr * s1a
    dg = sg * d1a + dg * s1a
    db = sb * d1a + db * s1a
    da = sa + da - 2 * sa * da

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_plus(src, dst):
    """
    Dca' = Sca × Da + Dca × Sa + Sca × (1 - Da) + Dca × (1 - Sa)
         = Sca + Dca
    Da'  = Sa × Da + Da × Sa + Sa × (1 - Da) + Da × (1 - Sa)
         = Sa + Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    dr = sr + dr
    dg = sg + dg
    db = sb + db
    da = sa + da

    composite = np.dstack((dr, dg, db, da))
    composite[composite > 1] = 1

    return composite


def comp_op_multiply(src, dst):
    """
    Dca' = Sca × Dca + Sca × (1 - Da) + Dca × (1 - Sa)
    Da'  = Sa × Da + Sa × (1 - Da) + Da × (1 - Sa)
         = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    s1a = 1 - sa
    d1a = 1 - da

    dr = sr * dr + sr * d1a + dr * s1a
    dg = sg * dg + sg * d1a + dg * s1a
    db = sb * db + sb * d1a + db * s1a
    da = sa + da - sa * da

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_screen(src, dst):
    """
    Dca' = (Sca × Da + Dca × Sa - Sca × Dca) + Sca × (1 - Da) + Dca × (1 - Sa)
         = Sca + Dca - Sca × Dca
    Da'  = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    dr = sr + dr - sr * dr
    dg = sg + dg - sg * dg
    db = sb + db - sb * db
    da = sa + da - sa * da

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_overlay(src, dst):
    """
    if 2 × Dca <= Da
        Dca' = 2 × Sca × Dca + Sca × (1 - Da) + Dca × (1 - Sa)
    otherwise
        Dca' = Sa × Da - 2 × (Da - Dca) × (Sa - Sca) + Sca × (1 - Da) + Dca × (1 - Sa)
             = Sca × (1 + Da) + Dca × (1 + Sa) - 2 × Dca × Sca - Da × Sa

    Da' = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1 - da
    s1a = 1 - sa
    sada = sa * da

    dr = np.where(
        2 * dr <= da,
        2 * sr * dr + sr * d1a + dr * s1a,
        sr * (1 + da) + dr * (1 + sa) - 2 * dr * sr - sada)
    dg = np.where(
        2 * dg <= da,
        2 * sg * dg + sg * d1a + dg * s1a,
        sg * (1 + da) + dg * (1 + sa) - 2 * dg * sg - sada)
    db = np.where(
        2 * db <= da,
        2 * sb * db + sb * d1a + db * s1a,
        sb * (1 + da) + db * (1 + sa) - 2 * db * sb - sada)
    da = sa + da - sada

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_darken(src, dst):
    """
    Dca' = min(Sca × Da, Dca × Sa) + Sca × (1 - Da) + Dca × (1 - Sa)
    Da'  = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1 - da
    s1a = 1 - sa

    dr = np.minimum(sr * da, dr * sa) + sr * d1a + dr * s1a
    dg = np.minimum(sg * da, dg * sa) + sg * d1a + dg * s1a
    db = np.minimum(sb * da, db * sa) + sb * d1a + db * s1a
    da = sa + da - sa * da

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_lighten(src, dst):
    """
    Dca' = max(Sca × Da, Dca × Sa) + Sca × (1 - Da) + Dca × (1 - Sa)
    Da'  = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1 - da
    s1a = 1 - sa

    dr = np.maximum(sr * da, dr * sa) + sr * d1a + dr * s1a
    dg = np.maximum(sg * da, dg * sa) + sg * d1a + dg * s1a
    db = np.maximum(sb * da, db * sa) + sb * d1a + db * s1a
    da = sa + da - sa * da

    composite = np.dstack((dr, dg, db, da))

    return composite


#
# def comp_op_color_dodge(src, dst):
#     """
#     if Sca == Sa and Dca == 0
#       Dca' = Sca × (1 - Da) + Dca × (1 - Sa)
#            = Sca × (1 - Da)
#     otherwise if Sca == Sa
#       Dca' = Sa × Da + Sca × (1 - Da) + Dca × (1 - Sa)
#     otherwise if Sca < Sa
#       Dca' = Sa × Da × min(1, Dca/Da × Sa/(Sa - Sca)) + Sca × (1 - Da) + Dca × (1 - Sa)
#
#     Da'  = Sa + Da - Sa × Da
#     """
#     assert src.shape == dst.shape
#
#     sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
#     dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]
#
#     d1a = 1 - da
#     s1a = 1 - sa
#     sada = sa * da
#
#     mr = sr == sa
#     dr[np.logical_and(mr, dr == 0)] = sr * d1a
#     dr[mr] = sada + sr * d1a + dr * s1a
#     dr[sr < sa] = \
#         sada * np.minimum(1, dr / da * sa / (sa - sr)) + sr * d1a + dr * s1a
#
#     mg = sg == sa
#     dr[np.logical_and(mg, dg == 0)] = sg * d1a
#     dr[mg] = sada + sg * d1a + dg * s1a
#     dr[sg < sa] = \
#         sada * np.minimum(1, dg / da * sa / (sa - sg)) + sg * d1a + dg * s1a
#
#     mb = sb == sa
#     dr[np.logical_and(mb, db == 0)] = sb * d1a
#     dr[mb] = sada + sb * d1a + db * s1a
#     dr[sb < sa] = \
#         sada * np.minimum(1, db / da * sa / (sa - sb)) + sb * d1a + db * s1a
#
#     da = sa + da - sada
#
#     composite = np.dstack((dr, dg, db, da))
#
#     return composite


def comp_op_hard_light(src, dst):
    """
    if 2 × Sca <= Sa
        Dca' = 2 × Sca × Dca + Sca × (1 - Da) + Dca × (1 - Sa)
    otherwise
        Dca' = Sa × Da - 2 × (Da - Dca) × (Sa - Sca) + Sca × (1 - Da) + Dca × (1 - Sa)
             = Sca × (1 + Da) + Dca × (1 + Sa) - Sa × Da - 2 × Sca × Dca

    Da'  = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1 - da
    s1a = 1 - sa
    sada = sa * da

    dr = np.where(
        2 * sr <= sa,
        2 * sr * dr + sr * d1a + dr * s1a,
        sr * (1 + da) + dr * (1 + sa) - 2 * dr * sr - sada)
    dg = np.where(
        2 * sg <= sa,
        2 * sg * dg + sg * d1a + dg * s1a,
        sg * (1 + da) + dg * (1 + sa) - 2 * dg * sg - sada)
    db = np.where(
        2 * sb <= sa,
        2 * sb * db + sb * d1a + db * s1a,
        sb * (1 + da) + db * (1 + sa) - 2 * db * sb - sada)
    da = sa + da - sada

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_difference(src, dst):
    """
    Dca' = abs(Dca × Sa - Sca × Da) + Sca × (1 - Da) + Dca × (1 - Sa)
         = Sca + Dca - 2 × min(Sca × Da, Dca × Sa)
    Da'  = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    sada = sa * da

    dr = sr + dr - 2 * np.minimum(sr * da, dr * sa)
    dg = sg + dg - 2 * np.minimum(sg * da, dg * sa)
    db = sb + db - 2 * np.minimum(sb * da, db * sa)
    da = sa + da - sada

    composite = np.dstack((dr, dg, db, da))

    return composite


def comp_op_exclusion(src, dst):
    """
    Dca' = (Sca × Da + Dca × Sa - 2 × Sca × Dca) + Sca × (1 - Da) + Dca × (1 - Sa)
    Da'  = Sa + Da - Sa × Da
    """
    assert src.shape == dst.shape

    sr, sg, sb, sa = src[..., 0], src[..., 1], src[..., 2], src[..., 3]
    dr, dg, db, da = dst[..., 0], dst[..., 1], dst[..., 2], dst[..., 3]

    d1a = 1 - da
    s1a = 1 - sa
    sada = sa * da

    dr = (sr * da + dr * sa - 2 * sr * dr) + sr * d1a + dr * s1a
    dg = (sg * da + dg * sa - 2 * sg * dg) + sg * d1a + dg * s1a
    db = (sb * da + db * sa - 2 * sb * db) + sb * d1a + db * s1a
    da = sa + da - sada

    composite = np.dstack((dr, dg, db, da))

    return composite
