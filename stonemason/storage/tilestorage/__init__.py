# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/22/15'

from .clusterfier import Clusterfier, ClusterStorage
from .concept import MetaTileStorageError, InvalidMetaTile, \
    InvalidMetaTileIndex, ReadOnlyMetaTileStorage, MetaTileKeyConcept, \
    MetaTileSerializeConcept, MetaTileStorageConcept
from .implements import NullMetaTileStorage, S3MetaTileStorage, \
    DiskMetaTileStorage, S3ClusterStorage, DiskClusterStorage

# XXX: for backward compatible
NullClusterStorage = NullMetaTileStorage
