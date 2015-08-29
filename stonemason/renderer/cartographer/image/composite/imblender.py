# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.composite.imblender
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of render node that compose image features by ImageMagick.
"""
__author__ = 'ray'
__date__ = '4/22/15'

import io
import os
import re
import subprocess

import six

from PIL import Image

from stonemason.renderer.engine.rendernode import CompositeNode
from stonemason.renderer.engine.context import RenderContext
from stonemason.util.tempfn import generate_temp_filename

from ..feature import ImageFeature

try:
    output = subprocess.check_output(['convert', '-version'])
except subprocess.CalledProcessError:
    raise ImportError("Cannot find ImageMagick convert command.")

__all__ = ['IMComposer', 'ImageMagickError']


class ImageMagickError(Exception):
    def __init__(self, ret, cmd, output=None):
        self.ret = ret
        self.cmd = cmd
        self.output = output

    def __str__(self):
        return '%d\n$ %s\n%s' % (self.ret, self.cmd, self.output)


class ImageMagickComposer(object):
    """ Compose, convert, transform images using `imagemagick`.

    Composer is implemented by export given `Image` to disk as file,
    and call imagemagick's convert command using :mod:`~subprocess`,
    then read the generated image file back.

    This method is not efficient but proves to be most stable, and since
    `imagemagick` itself is not known for its speed but for its versatile
    image processing commands, the extra iio and process spawning overhead
    is acceptable.

    For a complete composer command syntax, see imagemagick offical
    `CLI Manual`_ and `Usage Manual`_.

        .. _Usage Manual: http://www.imagemagick.org/Usage/
        .. _CLI Manual: http://www.imagemagick.org/script/command-line-options.php

    .. warning::

        `imagemagick` behavior is not consistent between versions,
        thus same command may produce slightly different results,
        so good luck!


    :param command: Command string sent to `imagemagick convert`, images are
        referenced using ``{{tag}}``, note the command should generate
        exactly one image.
    :type command: str

    :param export_format: Format used to export :class:`PIL.Image.Image` to
        image files, must be one of the format supported by `PIL` installation.
        Lossless format ``png`` or ``webp`` is recommended.
    :type export_format: str

    :param import_format: Format imagemagick use to write image files,  must
        be one of the format supported by `PIL` installation.  Uncompressed
        format like ``tiff`` is recommended.
    :type import_format: str

    :param tempdir: Directory of temporary image files will be written, by
        default, system temporary directory will be used.  Specify a fast
        SSD volume or memory disk is recommended.
    :type tempdir: str or None
    """

    def __init__(self,
                 command,
                 export_format='png',
                 import_format='png',
                 tempdir=None,
                 ):
        self._export_format = export_format
        self._import_format = import_format
        self._tempdir = tempdir
        self._command = self.parse_command(command)

    def compose(self, images):
        """ Compose given `images` using composer command.

        :param images: A dict of ``(tag, image)``. ``tag`` is specified in
            composer command, while ``image`` is a :class:`PIL.Image.Image`
            instance.
        :type images: dict
        :return: composed image.
        :rtype: :class:`PIL.Image.Image`
        :raise: ImageMagickError
        """
        # make a copy since we will modify it in-place
        command = list(self._command)

        # remember tempfiles generated
        files_to_delete = dict()

        for i, tag in self.subs_command(command):

            try:
                image = images[tag]
            except KeyError:
                raise KeyError('Invalid image reference "%s"' % tag)
            assert isinstance(image, Image.Image)

            # generate a new tempfile for each image
            if tag not in files_to_delete:
                prefix = 'stonemasonmgk~%s~' % tag
                filename = generate_temp_filename(dirname=self._tempdir,
                                                  prefix=prefix,
                                                  suffix='.' + self._import_format)

                # delete the temp file later
                files_to_delete[tag] = filename

                # write image data to temp file
                image.save(filename, self._export_format)

            # Replace {{tag}} with generated filename
            command[i] = files_to_delete[tag]

        try:
            # HACK: fixes OpenMP error under ubuntu-14.04 or higher,
            # don't need openmp anyway since rendering will be threaded.
            env = os.environ.copy()
            env['OMP_THREAD_LIMIT'] = '1'
            # call imagemagick command
            process = subprocess.Popen(command,
                                       env=env,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            retcode = process.poll()
            if retcode:
                raise ImageMagickError(retcode, ' '.join(command),
                                       output=stderr)

            return Image.open(io.BytesIO(stdout))
        finally:
            # delete temporary files
            for filename in six.itervalues(files_to_delete):
                os.unlink(filename)

    def parse_command(self, command):
        # default imagemagick options
        lines = ['convert -quiet -limit thread 1']
        for line in command.splitlines():
            if line.lstrip().startswith('#'):
                continue  # skip comment
            line = line.strip()
            if line:
                lines.append(line)
        lines.append('%s:-' % self._export_format)
        return ' '.join(lines).split()

    def subs_command(self, command):
        for i in range(len(command)):
            arg = command[i]
            match = re.match(r'<<(\w+)>>', arg)
            if match:
                tag = match.group(1)
                yield (i, tag)


class IMComposer(CompositeNode):
    """ImageMagick Composite Render Node

    The `IMComposer` composes image feature produced by source render nodes by
    `ImageMagick` command.

    Below is a complex composer command which generates a `newspaper` effect
    with variable depth label haloing from for mapnik rendered images::

        # Apply ordered dither to landbase, mimics 'halftone dither' effect
        ( <<base>> -ordered-dither o8x8,4 )

        (
            # Use a different dither for some variation
            ( <<road>> )
            # Fill halo with land color and only render on top of roads
            ( <<label>> -channel A
            -morphology Dilate Disk:4
            +channel
            +level-colors #ebe9e6
            ) -compose Atop -composite -ordered-dither o4x4,4
        ) -compose Over -composite

        (
            # Increase lightness of labels, Multiply later...
            <<label>>
            -brightness-contrast +10
            # Mimics 'typewriter' effect, only works on thin fonts.
            # Find line joins of labels and thicken/darken them.
            # Uses ImageMagick's morphology operation, slow!
            ( +clone -channel A
              -morphology HMT LineJunctions
              -morphology Dilate Disk:1
              +channel
            ) -compose Multiply -composite
        )  -compose Darken -composite

        # Make "real" duotone effect, not fake color tint.
        # Convert to grayscale then apply duotone lookup table.

        # The reference duotone images are converted from
        # Photoshop's classic 'Duotone' mode library.
        -brightness-contrast -12x-10
        -colorspace gray Bl-for-dark-cg9-cg2.png -clut

        # Finally, convert to paletted PNG format
        -dither none
        -colors 128

    .. figure:: _static/newspaper.png
       :width: 100 %
       :alt: "Newspaper" map sample render
       :align: center

       Sample render using 4 mapnik layers and imagemagick composer


    :param name: a string literal that identifies the node
    :type name: str

    :param nodes: a list of two source render nodes.
    :type nodes: list

    :param command: Command string sent to `imagemagick convert`, images are
        referenced using ``{{tag}}``, note the command should generate
        exactly one image.
    :type command: str

    :param tempdir: Directory of temporary image files will be written, by
        default, system temporary directory will be used.  Specify a fast
        SSD volume or memory disk is recommended.
    :type tempdir: str or None

    :param tempfmt: Format imagemagick use to write image files,  must
        be one of the format supported by `PIL` installation.  Uncompressed
        format like ``tiff`` is recommended.
    :type tempfmt: str

    """
    def __init__(self, name, nodes, command=None, tempdir=None, tempfmt='png'):
        CompositeNode.__init__(self, name, nodes)
        self._composer = ImageMagickComposer(
            command,
            export_format=tempfmt,
            import_format=tempfmt,
            tempdir=tempdir)

    def render(self, context):
        assert isinstance(context, RenderContext)

        sources = dict((l.name, l.render(context).data) for l in self._nodes)

        result = self._composer.compose(sources)

        return ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=result)
