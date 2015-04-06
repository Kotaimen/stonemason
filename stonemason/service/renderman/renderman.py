# -*- encoding: utf-8 -*-


"""
    stonemason.service.renderman.renderman
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Multiprocessing based tile renderer.

    A direct port of old mason tilerenderer.py
"""

__author__ = 'kotaimen'
__date__ = '4/3/15'

import multiprocessing
import multiprocessing.pool
import multiprocessing.sharedctypes
import multiprocessing.queues
import collections
import ctypes
import time
import logging

from stonemason.mason import Mason, MasonMap
from stonemason.mason.theme import MemThemeManager, FileSystemThemeLoader, MapTheme
from stonemason.pyramid import Pyramid
from stonemason.pyramid.geo import TileMapSystem
from stonemason.util.timer import Timer, human_duration

from .walkers import create_walker

#
# Constants
#
CPU_COUNT = multiprocessing.cpu_count()
QUEUE_LIMIT = 100

#
# Global logger
#
logger = None


#
# Helpers
#

class RenderDirective(collections.namedtuple(
    '_RenderDirective',
    '''themes theme_name
       levels envelope csv
       workers logfile''')):
    """Render directive from CLI command."""
    pass


class Stats(ctypes.Structure):
    """Rendering progress and stats.

    Must be a :class:`ctypes.Structure` to share between processes using
    :mod:`multiprocessing.sharedctypes`.
    """

    _fields_ = [
        ('progress', ctypes.c_longlong),
        ('rendered', ctypes.c_longlong),
        ('failed', ctypes.c_longlong),
        ('total_time', ctypes.c_float),
    ]

    def __init__(self):
        ctypes.Structure.__init__(self)
        self.progress = 0
        self.rendered = 0
        self.failed = 0
        self.time_taken = 0


def create_mason(directive):
    """Create a new Mason facade instance from render directive."""
    assert isinstance(directive, RenderDirective)

    theme_manager = MemThemeManager()
    theme_loader = FileSystemThemeLoader(directive.themes)
    theme_loader.load_into(theme_manager)

    mason = Mason()
    theme = theme_manager.get(directive.theme_name)
    if theme is None:
        raise RuntimeError('Theme "%s" not found' % directive.theme_name)

    assert isinstance(theme, MapTheme)
    mason.load_map_from_theme(theme)

    return mason


def setup_logger(log_file='render.log', level=logging.WARNING):
    global logger
    if logger is not None:
        return

    # borrow multiprocessing's logger so we can reliably write to console
    logger = multiprocessing.log_to_stderr(level=logging.INFO)

    # also attach a file handler for warning and errors
    formatter = logging.Formatter(
        '[%(asctime)s - %(levelname)s/%(processName)s] %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)


#
# Process modules
#

def walker(directive, queue, stats):
    """ Spawn MetaTileIndexes into the queue using specified walker"""
    assert isinstance(directive, RenderDirective)
    assert isinstance(queue, multiprocessing.queues.Queue)
    # assert isinstance(stats, Stats)

    setup_logger(directive.logfile)

    mason = create_mason(directive)

    # XXX: Mason should provide getters, and MasonMap is a really bad name...
    mason_map = mason.get_map(directive.theme_name)
    assert isinstance(mason_map, MasonMap)
    pyramid = mason_map.provider.pyramid
    assert isinstance(pyramid, Pyramid)

    tms = TileMapSystem(pyramid)
    walker = create_walker(tms,
                           directive.levels,
                           pyramid.stride,
                           directive.envelope,
                           directive.csv)

    logger.info('Started spawning metatiles from #%d' % stats.progress)

    # put indexes into the queue
    for n, index in enumerate(walker, start=1):
        # if n < stats.progress:
        # continue
        queue.put(index)
    else:
        logger.info('Stopped after spawn #%d metatiles.' % n)


def renderer(directive, queue, stats):
    assert isinstance(directive, RenderDirective)
    assert isinstance(queue, multiprocessing.queues.Queue)
    # assert isinstance(stats, Stats)

    setup_logger(directive.logfile)

    mason = create_mason(directive)

    while True:
        index = queue.get()

        # render completed
        if index is None:
            break

        logger.info('Rendering %s', repr(index))

        with Timer('  %s rendered in %%(time)s' % repr(index),
                   writer=logger.info, newline=False) as timer:
            try:
                data = mason.get_tile(directive.theme_name,
                                      index.z,
                                      index.x,
                                      index.y)
            except Exception as e:
                stats.failed += 1
                logger.exception('Error while rendering %s' % repr(index))
            finally:
                queue.task_done()

        stats.total_time += timer.get_time()
        if data:
            stats.rendered += 1
        else:
            stats.skipped += 1


def harbinger(directive):
    pass


#
# Entry Point
#
def renderman(directive):
    assert isinstance(directive, RenderDirective)
    setup_logger(directive.logfile)

    # shared stats
    stats = multiprocessing.sharedctypes.Value(Stats)
    # job queue
    queue = multiprocessing.JoinableQueue(maxsize=QUEUE_LIMIT)

    # start the tileindex spawner as producer
    producer = multiprocessing.Process(name='producer',
                                       target=walker,
                                       args=(directive, queue, stats))

    producer.daemon = True
    producer.start()

    # create all renderer processes
    workers = []
    for n in range(directive.workers):
        logging.info('Creating renderer#%d', n)
        worker = multiprocessing.Process(name='renderer#%d' % n,
                                         target=renderer,
                                         args=(directive, queue, stats))
        worker.daemon = True
        workers.append(worker)

    # wait until the queue is well populated
    for i in range(10):
        time.sleep(0.1)
        if not queue.empty():
            break

    # start all workers, one by one to avoid stashing io
    for n, worker in enumerate(workers):
        worker.start()
        logging.info('Started renderer#%d', n)
        time.sleep(0.1)

    try:
        producer.join()
        queue.join()
    except KeyboardInterrupt:
        logger.info('===== Canceled =====')
    else:
        logger.info('===== Completed =====')
    finally:
        # return unwrapped object
        return stats.get_obj()
