# -*- encoding: utf-8 -*-
"""
    stonemason.storage.backends.s3
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements s3 backend for storage module.
"""
__author__ = 'ray'
__date__ = '10/22/15'

import time
import six
import boto3
import botocore.exceptions

from stonemason.storage.concept import PersistentStorageConcept


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

    def __init__(self, access_key=None, secret_key=None, bucket='my_bucket',
                 policy='private', reduced_redundancy=False):
        self._s3 = boto3.resource('s3',
                                  aws_access_key_id=access_key,
                                  aws_secret_access_key=secret_key)

        self._bucket_name = bucket

        self._bucket = self._s3.Bucket(bucket)
        self._bucket.load()  # ensure bucket exists

        assert policy in ['private', 'public-read']
        self._policy = policy

        self._storage_class = 'STANDARD'
        if reduced_redundancy:
            self._storage_class = 'REDUCED_REDUNDANCY'

    def exists(self, key):
        item = self._s3.Object(self._bucket_name, key)
        try:
            item.load()
        except botocore.exceptions.ClientError:
            return False
        else:
            return True

    def retrieve(self, key):
        item = self._s3.Object(self._bucket_name, key)

        # Check key existence first otherwise get_content() will
        # retry several times, which slows thing down a lot.
        try:
            item.load()
        except botocore.exceptions.ClientError:
            return None, None

        response = item.get()

        blob = response['Body'].read()
        metadata = response['Metadata']
        metadata['LastModified'] = float(
            time.mktime(item.last_modified.timetuple()))

        return blob, metadata

    def store(self, key, blob, metadata):
        assert isinstance(key, six.string_types)
        assert isinstance(blob, bytes)
        assert isinstance(metadata, dict)

        item = self._s3.Object(self._bucket_name, key)
        item.put(
            ACL=self._policy,
            Body=blob,
            Metadata=metadata,
            StorageClass=self._storage_class,
        )

    def retire(self, key):
        item = self._s3.Object(self._bucket_name, key)
        item.delete()

    def close(self):
        del self._s3
