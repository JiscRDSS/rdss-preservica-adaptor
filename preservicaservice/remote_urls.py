import abc
from urllib.parse import urlparse

import boto3
import botocore.exceptions
import requests

from .errors import UnderlyingSystemError, ResourceNotFoundError


class BaseRemoteUrl(abc.ABC):
    """ Wrapper for remote files."""

    def __init__(self, url):
        self.url = url

    @property
    def host(self):
        return urlparse(self.url).netloc

    @property
    def path(self):
        return urlparse(self.url).path.lstrip('/')

    @classmethod
    @abc.abstractmethod
    def parse(cls, url):
        """ Factory method to produce a url from string.

        All validation should happen here.

        :param string url: remote URL
        :raise: ValueError if any error
        :return: instance
        :rtype: BaseRemoteUrl
        """

    @abc.abstractmethod
    def download(self, download_path):
        """ Download remote file to provided path.
        :param download_path: path on local filesystem to download file to.
        :type download_path: string
        :raise: ResourceNotFoundError if any error
        """


class S3RemoteUrl(BaseRemoteUrl):
    """ Wrapper for remote S3 files."""

    @classmethod
    def parse(cls, url):
        """ Parse URL to an S3RemoteUrl object.

        :param string url: remote URL to remote S3 object.
        """
        p = urlparse(url)
        if not bool(p.scheme == 's3' and p.netloc):
            raise ValueError(
                'fileStorageLocation is invalid: {}'.format(url),
            )
        return cls(url)

    def _get_bucket(self, bucket_name):
        """ Retrieve bucket by name."""
        session = boto3.Session()
        s3 = session.resource('s3')
        return s3.Bucket(bucket_name)

    def download(self, download_path):
        """ Download remote file from S3 to the provided download path."""
        bucket = self._get_bucket(self.host)
        try:
            bucket.download_file(self.path, download_path)
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                raise ResourceNotFoundError(
                    'resource not found in S3: {}'.format(e),
                )
            else:
                raise UnderlyingSystemError(
                    'unable to download resource from S3: {}'.format(e),
                )


class HTTPRemoteUrl(BaseRemoteUrl):
    """ Wrapper for remote HTTP files."""

    @classmethod
    def parse(cls, url):
        """ Parse URL to an S3RemoteUrl object.

        :param string url: remote URL to remote S3 object.
        """
        valid_schemes = ['http', 'https']
        p = urlparse(url)
        if not bool(p.scheme in valid_schemes and p.netloc):
            raise ValueError('invalid URL {}'.format(url))
        return cls(url)

    def download(self, download_path):
        """ Download remote file via HTTP to the provided download path."""
        try:
            r = requests.get(self.url, stream=True)
            with open(download_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except requests.RequestException as re:
            raise UnderlyingSystemError(
                'unable to download resource via HTTP: {}'.format(re),
            )
