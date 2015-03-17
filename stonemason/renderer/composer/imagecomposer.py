# -*- encoding: utf-8 -*-

"""
    stonemason.renderer.composer.imagecomposer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Composing images
"""

__author__ = 'kotaimen'
__date__ = '3/16/15'

class ComposerError(RuntimeError):
    pass

class ImageComposer(object):
    """ Convert, transform or compose a list of images using underlying imaging
    processing engine."""

    def compose(self, image_list):
        """ Compose given `images` using composer command.

        :param images: A dict of ``(tag, image)``. ``tag`` is specified in
            composer command, while ``image`` is a :class:`PIL.Image.Image`
            instance.
        :type images: dict
        :return: composed image.
        :rtype: :class:`PIL.Image.Image`
        """
        raise NotImplementedError
