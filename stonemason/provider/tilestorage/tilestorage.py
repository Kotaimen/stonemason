# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/18/15'

"""
    stonemason.provider.tilestorage.tilestorage
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Persistence storage of tiles.
"""


class TileStorageError(Exception):
    pass


class InvalidMetaTileIndex(TileStorageError):
    pass


class InvalidMetaTile(TileStorageError):
    pass


class ReadonlyStorage(TileStorageError):
    pass


class ClusterStorage(object):  # pragma: no cover
    """Homologous persistence storage of `TileCluster`.

    Homologous means single storage can only store single type of TileClusters.
    All MetaTiles put into the storage must have same `mimetype`, `stride` and
    `buffering`.
    """

    def get(self, index):
        """Retrieve a `TileCluster` from the storage.

        Retrieve a `TileCluster` from the storage, returns ``None`` if its not
        found ind the storage

        :param index: MetaTile index of the tile cluster.
        :type index: :class:`~stonemason.provider.tilestorage.MetaTileIndex`
        :returns: Retrieved TileCluster.
        :rtype: :class:`~stonemason.provider.tilestorage.TileCluster` or ``None``
        """
        raise NotImplementedError

    def put(self, metatile):
        """Store a `MetaTile` in the storage as `TileCluster`.

        Store a `MetaTile` in the storage as `TileCluster`, overriding
        any existing one.

        :param metatile: MetaTile to store.
        :type metatile: :class:`~stonemason.provider.pyramid.MetaTile`
        """

        raise NotImplementedError

    def retire(self, index):
        """Delete `TileCluster` with given index.

        If `TileCluster` does not present in cache, this operation has no effect.


        :param index: MetaTile index of the TileCluster.
        :type index: :class:`~stonemason.provider.tilestorage.MetaTileIndex`
        """
        raise NotImplementedError


class MetaTileStorage(object):  # pragma: no cover
    """Persistence storage of `MetaTile`."""

    def get(self, index):
        """Retrieve a `MetaTile` from the storage.

        Retrieve a `MetaTile` from the storage, returns ``None`` if its not
        found ind the storage

        :param index: MetaTile index of the MetaTile.
        :type index: :class:`~stonemason.provider.tilestorage.MetaTileIndex`
        :returns: Retrieved tile cluster.
        :rtype: :class:`~stonemason.provider.tilestorage.MetaTile`
        """
        raise NotImplementedError

    def put(self, metatile):
        """Store a `MetaTile` in the storage.

        Store a `MetaTile` in the storage, overriding any existing one.

        :param metatile: MetaTile to store.
        :type metatile: :class:`~stonemason.provider.pyramid.MetaTile`
        """

        raise NotImplementedError

    def retire(self, index):
        """Delete `MetaTile` with given index.

        If `MetaTile` does not present in cache, this operation has no effect.


        :param index: MetaTile index of the tile cluster.
        :type index: :class:`~stonemason.provider.tilestorage.MetaTileIndex`
        """
        raise NotImplementedError


class NullClusterStorage(ClusterStorage):
    """A storage stores nothing."""

    def get(self, index):
        return None

    def put(self, metatile):
        return

    def retire(self, index):
        return


class NullMetaTileStorage(MetaTileStorage):
    """A storage stores nothing."""

    def get(self, index):
        return None

    def put(self, metatile):
        return

    def retire(self, index):
        return
