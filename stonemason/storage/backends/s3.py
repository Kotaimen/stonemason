# -*- encoding: utf-8 -*-
"""
    stonemason.storage.backends.s3
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements s3 backend for storage module.
"""
__author__ = 'ray'
__date__ = '10/22/15'

import time
import email
import boto
import six

from boto.s3.key import Key

from stonemason.storage.concept import PersistentStorageConcept


def s3timestamp2mtime(timestamp):
    """Convert RFC 2822 datetime string used by s3 to mtime."""
    modified = email.utils.parsedate_tz(timestamp)
    if modified is None:
        return None
    mtime = email.utils.mktime_tz(modified)
    return float(mtime)


def mtime2s3timestamp(mtime):
    """Convert mtime to RFC 2822 datetime string."""
    return email.utils.formatdate(time.time())


class S3Storage(PersistentStorageConcept):
    """S3 Storage

    The ``S3Storage`` uses AWS Simple Storage Service as persistence backend.

    :param access_key: AWS access key id, if set to `None`, try load
        from environment variable ``AWS_ACCESS_KEY_ID``, or IAM role temporary
        security credentials.
    :type access_key: str or ``None``

    :param secret_key: AWS secret key id, if set to `None`, try load
        from environment variable ``AWS_SECRET_ACCESS_KEY``, or IAM role
        temporary security credentials.
    :type secret_key: str or ``None``

    :param bucket: Required, s3 bucket name, the bucket must be created
        first with proper permissions, policy, lifecycle management,
        visioning, sever side encryption, and redundancy level.
    :type bucket: str

    :param policy: Canned policy, must be one of:

        `private`
            Owner gets full control, no one else has access rights.

        `public-read`
            Owner gets full control, no one else has read rights.

    :type policy: str

    :param reduced_redundancy: Set storage class to REDUCED_REDUNDANCY
        if set to `True`, default is `False`

    :type reduced_redundancy: bool

    """

    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', policy='private',
                 reduced_redundancy=False):
        self._conn = boto.connect_s3(aws_access_key_id=access_key,
                                     aws_secret_access_key=secret_key, )
        self._bucket = self._conn.get_bucket(bucket_name=bucket)

        assert policy in ['private', 'public-read']
        self._policy = policy
        self._reduced_redundancy = reduced_redundancy

    def exists(self, key):
        s3key = Key(bucket=self._bucket, name=key)
        return s3key.exists()

    def retrieve(self, key):
        s3key = Key(bucket=self._bucket, name=key)
        if not s3key.exists():
            # Check key existence first otherwise get_content() will
            # retry several times, which slows thing down a lot.
            return None, None
        blob = s3key.get_contents_as_string()
        if six.PY2:
            etag = s3key.md5
        else:
            # Key.md5 returns bytes on py3 despite it is actually a hex string
            etag = s3key.md5.decode()
        metadata = dict(etag=etag,
                        mimetype=s3key.content_type,
                        mtime=s3timestamp2mtime(s3key.last_modified))

        return blob, metadata

    def store(self, key, blob, metadata):
        assert isinstance(key, six.string_types)
        assert isinstance(blob, bytes)
        assert isinstance(metadata, dict)
        assert 'mimetype' in metadata
        assert 'etag' in metadata
        assert 'mtime' in metadata

        s3key = Key(bucket=self._bucket, name=key)
        s3key.content_type = metadata['mimetype']
        s3key.md5 = metadata['etag']
        s3key.last_modified = mtime2s3timestamp(metadata['mtime'])
        s3key.set_contents_from_string(blob,
                                       replace=True,
                                       policy=self._policy,
                                       reduced_redundancy=self._reduced_redundancy)

    def retire(self, key):
        s3key = Key(bucket=self._bucket, name=key)
        s3key.delete()

    def close(self):
        self._conn.close()
