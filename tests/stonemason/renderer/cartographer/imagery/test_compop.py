# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/6/15'

import os

from tests import DATA_DIRECTORY, ImageTestCase, skipUnlessHasScipy, \
    skipUnlessHasSkimage, carto

if carto.HAS_SCIPY and carto.HAS_SKIMAGE:
    from stonemason.renderer.cartographer.imagery.compop import *


@skipUnlessHasScipy()
@skipUnlessHasSkimage()
class TestAlphaComposite(ImageTestCase):
    def setUp(self):
        src = test_image_1()
        dst = test_image_2()

        # normalize and premultiply
        self.src = premultiply(skimage.img_as_float(src))
        self.dst = premultiply(skimage.img_as_float(dst))

        self.work_dir = os.path.join(DATA_DIRECTORY, 'composite')

    def test_clear(self):
        composite = demultiply(comp_op_clear(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_clear.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_clear.png'))

        self.assertImageEqual(expected, actually)

    def test_src(self):
        composite = demultiply(comp_op_src(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_src.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_src.png'))

        self.assertImageEqual(expected, actually)

    def test_dst(self):
        composite = demultiply(comp_op_dst(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_dst.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_dst.png'))

        self.assertImageEqual(expected, actually)

    def test_src_over(self):
        composite = demultiply(comp_op_src_over(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_src_over.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_src_over.png'))

        self.assertImageEqual(expected, actually)

    def test_dst_over(self):
        composite = demultiply(comp_op_dst_over(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_dst_over.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_dst_over.png'))

        self.assertImageEqual(expected, actually)

    def test_src_in(self):
        composite = demultiply(comp_op_src_in(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_src_in.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_src_in.png'))

        self.assertImageEqual(expected, actually)

    def test_dst_in(self):
        composite = demultiply(comp_op_dst_in(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_dst_in.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_dst_in.png'))

        self.assertImageEqual(expected, actually)

    def test_src_atop(self):
        composite = demultiply(comp_op_src_atop(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_src_atop.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_src_atop.png'))

        self.assertImageEqual(expected, actually)

    def test_dst_atop(self):
        composite = demultiply(comp_op_dst_atop(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_dst_atop.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_dst_atop.png'))

        self.assertImageEqual(expected, actually)

    def test_src_out(self):
        composite = demultiply(comp_op_src_out(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_src_out.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_src_out.png'))

        self.assertImageEqual(expected, actually)

    def test_dst_out(self):
        composite = demultiply(comp_op_dst_out(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_dst_out.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_dst_out.png'))

        self.assertImageEqual(expected, actually)

    def test_xor(self):
        composite = demultiply(comp_op_xor(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_xor.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_xor.png'))

        self.assertImageEqual(expected, actually)


@skipUnlessHasScipy()
@skipUnlessHasSkimage()
class TestMathComposite(ImageTestCase):
    def setUp(self):
        src = test_image_4()
        dst = test_image_3()

        # normalize and premultiply
        self.src = premultiply(skimage.img_as_float(src))
        self.dst = premultiply(skimage.img_as_float(dst))

        self.work_dir = os.path.join(DATA_DIRECTORY, 'composite')

    def test_plus(self):
        composite = demultiply(comp_op_plus(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_plus.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_plus.png'))

        self.assertImageEqual(expected, actually)

    def test_multiply(self):
        composite = demultiply(comp_op_multiply(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_multiply.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_multiply.png'))

        self.assertImageEqual(expected, actually)

    def test_screen(self):
        composite = demultiply(comp_op_screen(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_screen.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_screen.png'))

        self.assertImageEqual(expected, actually)

    def test_overlay(self):
        composite = demultiply(comp_op_overlay(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_overlay.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_overlay.png'))

        self.assertImageEqual(expected, actually)

    def test_darken(self):
        composite = demultiply(comp_op_darken(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_darken.png'))

        expected = Image.open(os.path.join(self.work_dir, 'comp_op_darken.png'))

        self.assertImageEqual(expected, actually)

    def test_lighten(self):
        composite = demultiply(comp_op_lighten(self.src, self.dst))
        composite = skimage.img_as_ubyte(composite)

        actually = Image.fromarray(composite, mode='RGBA')
        # actually.save(os.path.join(self.work_dir, 'comp_op_lighten.png'))

        expected = Image.open(
            os.path.join(self.work_dir, 'comp_op_lighten.png'))

        self.assertImageEqual(expected, actually)
