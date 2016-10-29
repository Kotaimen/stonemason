# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/22/15'

try:
    from urllib.parse import urlparse, parse_qsl
except ImportError:
    # for python2.7
    from urlparse import urlparse, parse_qsl


from .concept import *
from .implement import *

def create_feature_storage(conn_string):
    try:
        components = urlparse(conn_string)
        dialect, backend = components.scheme.split('+')
        prefix = components.path
        params = dict(parse_qsl(components.query))
    except Exception as e:
        raise ValueError('''
            Connection string usages: dialect+backend://[bucket]/path[?query]
        ''')

    if backend == 's3':
        bucket = components.netloc
        if prefix.startswith('/'):
            prefix = prefix[1:]
        if dialect == 'raster':
            return S3RasterStorage(bucket=bucket, prefix=prefix, **params)
    elif backend == 's3http':
        bucket = components.netloc
        if prefix.startswith('/'):
            prefix = prefix[1:]
        if dialect == 'raster':
            return S3HttpRasterStorage(bucket=bucket, prefix=prefix, **params)

    elif backend == 'disk':
        if dialect == 'raster':
            return DiskRasterStorage(prefix=prefix, **params)

    else:
        raise ValueError('Unknown backend: %s' % conn_string)
