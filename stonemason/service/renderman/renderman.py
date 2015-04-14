# -*- encoding: utf-8 -*-


"""
    stonemason.service.renderman.renderman
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Multiprocessing based tile renderer.

    A direct port of old mason tilerenderer.py, using vanilla multiprocessing,
    since it enables customising process initialization.
"""

__author__ = 'kotaimen'
__date__ = '4/3/15'

import multiprocessing
import multiprocessing.pool
import multiprocessing.sharedctypes
import multiprocessing.queues
import time
import logging

from stonemason.mason import Mason, Portrayal, MasonTileVisitor, \
    MasonMetaTileFarm
from stonemason.mason.theme import MemGallery, FileSystemCurator, Theme
from stonemason.pyramid import Pyramid, MetaTileIndex
from stonemason.pyramid.geo import TileMapSystem
from stonemason.util.timer import Timer, human_duration

from .script import RenderScript, RenderStats
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


def create_mason(script):
    """Create a new Mason facade instance from render directive."""
    assert isinstance(script, RenderScript)

    theme_gallery = MemGallery()
    theme_loader = FileSystemCurator(script.gallery)
    theme_loader.add_to(theme_gallery)

    mason = Mason()
    theme = theme_gallery.get(script.theme_name)
    if theme is None:
        raise RuntimeError(
            'Theme "%s %s" not found' % (script.theme_name, script.schema_tag))

    assert isinstance(theme, Theme)
    mason.load_portrayal_from_theme(theme)

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

def walker(script, queue, stats):
    """ Spawn MetaTileIndexes into the queue using specified walker"""
    assert isinstance(script, RenderScript)
    assert isinstance(queue, multiprocessing.queues.Queue)
    # assert isinstance(stats, Stats)

    setup_logger(script.log_file)

    mason = create_mason(script)

    # XXX: Mason should provide getters, and MasonMap is a really bad name...
    portrayal = mason.get_portrayal(script.theme_name)
    assert isinstance(portrayal, Portrayal)
    pyramid = portrayal.pyramid
    assert isinstance(pyramid, Pyramid)

    tms = TileMapSystem(pyramid)
    walker = create_walker(script, tms)

    logger.info('Started spawning metatiles from #%d' % stats.progress)

    # put indexes into the queue
    for n, index in enumerate(walker, start=1):
        # if n < stats.progress:
        # continue
        queue.put(index)
    else:
        logger.info('Stopped after spawn #%d metatiles.' % n)


def renderer(script, queue, stats):
    assert isinstance(script, RenderScript)
    assert isinstance(queue, multiprocessing.queues.Queue)
    # assert isinstance(stats, Stats)

    setup_logger(script.log_file)

    mason = create_mason(script)
    visitor = MasonMetaTileFarm(mason)

    while True:
        index = queue.get()

        # render completed
        if index is None:
            break

        assert isinstance(index, MetaTileIndex)

        logger.info('Rendering %s', repr(index))

        with Timer('  %s rendered in %%(time)s' % repr(index),
                   writer=logger.info, newline=False) as timer:
            try:
                result = visitor.render_metatile(script.theme_name,
                                                 script.schema_tag,
                                                 index.z,
                                                 index.x,
                                                 index.y,
                                                 index.stride)
            except Exception as e:
                stats.failed += 1
                logger.exception('Error while rendering %s' % repr(index))
                raise
            finally:
                queue.task_done()
                stats.progress += 1

        stats.total_time += timer.get_time()
        if result:
            stats.rendered += 1
        else:
            stats.skipped += 1


#
# Entry Point
#
def renderman(script):
    """Start a new render job using given `script`, block until render
    completes, and returns render status.

    :param script: Render script defines the render job
    :type script: :class:`~stonemason.service.renderman.RenderScript`
    :return: Render status.
    :rtype: :class:`~stonemason.service.renderman.RenderStats`
    """

    assert isinstance(script, RenderScript)
    setup_logger(script.log_file)

    # shared stats
    stats = multiprocessing.sharedctypes.Value(RenderStats)
    # job queue
    queue = multiprocessing.JoinableQueue(maxsize=QUEUE_LIMIT)

    # start the tileindex spawner as producer
    producer = multiprocessing.Process(name='producer',
                                       target=walker,
                                       args=(script, queue, stats))

    producer.daemon = True
    producer.start()

    # create all renderer processes
    workers = []
    for n in range(script.workers):
        logging.info('Creating renderer#%d', n)
        worker = multiprocessing.Process(name='renderer#%d' % n,
                                         target=renderer,
                                         args=(script, queue, stats))
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
        # return unwrapped ctypes object
        return stats.get_obj()
