# -*- encoding: utf-8 -*-

"""
    stonemason.services.renderman.script
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Render job and status.
"""

__author__ = 'kotaimen'
__date__ = '4/9/15'

import ctypes
import collections


_RenderScript = collections.namedtuple(
    '_RenderScript',
    '''
    gallery theme_name schema_tag
    levels envelope csv_file
    workers log_file
    progress
    ''')


class RenderScript(_RenderScript):
    """Describes requirement of a render job.

    This is a immutable :class:`~multiprocessing.namedtuple` thus can be
    passed around subprocesses.

    .. seealso:: :class:`~stonemason.pyramid.Pyramid`,
        :class:`~stonemason.pyramid.geo.TileMapSystem`,
        :class:`~stonemason.pyramid.MetaTileIndex`,
        :class:`~stonemason.pyramid.geo.Envelope`,
        :class:`~stonemason.pyramid.geo.TileMapSystem`,
        :class:`~stonemason.services.renderman.PyramidWalker`.

    :param gallery: Gallery root directory.
    :type gallery: str

    :param theme_name: Name of the theme to render.
    :type theme_name: str

    :param schema_tag: Tag of the schema to render.
    :type schema_tag: str

    :param levels: A list of Tile levels to render.
    :type levels: list

    :param envelope: A envelope in geographic coordinate system defines
        a rectangular area to render.
    :type envelope: tuple

    :param csv: A CSV file contains list of MetaTiles to render.
    :type csv: str

    :param workers: Number of renderer workers.
    :type workers: int

    :param logfile: Logfile to write errors.
    :type logfile: str

    :param progress: Start render from given progress.
    :type progress: int
    """

    def __new__(cls, gallery='', theme_name='', schema_tag='',
                levels=None, envelope=(), csv_file=None,
                workers=1, log_file=None, progress=0):
        return _RenderScript.__new__(cls,
                                     gallery, theme_name, schema_tag,
                                     levels, envelope, csv_file,
                                     workers, log_file, progress)


class RenderStats(ctypes.Structure):
    """Progress and status of a render job.

    This is a :class:`ctypes.Structure` which is designed to be shared
    between processses using :mod:`multiprocessing.sharedctypes`.

    """

    _fields_ = [
        ('progress', ctypes.c_longlong),
        ('rendered', ctypes.c_longlong),
        ('failed', ctypes.c_longlong),
        ('total_time', ctypes.c_float),
    ]

    def __init__(self):
        ctypes.Structure.__init__(self)

        #: Number of `MetaTiles` successfully rendered.
        self.progress = 0
        #: Number of successfully rendered `MetaTiles`.
        self.rendered = 0
        #: Number of `MetaTiles` failed to render.
        self.failed = 0
        #: Total CPU time taken by renderers in seconds.
        self.total_time = 0
