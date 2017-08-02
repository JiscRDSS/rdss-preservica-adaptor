import moto
import pytest

from preservicaservice import tasks
from preservicaservice.s3_url import S3Url
from .helpers import create_bucket


@pytest.fixture
def task():
    yield tasks.MetadataDeleteTask(S3Url('s3://bucket/prefix/foo'))


@moto.mock_s3
def test_delete_existing(task, valid_config):
    bucket = create_bucket()
    bucket.put_object(Key='prefix/foo', Body='bar')
    task.run(valid_config)
    assert 'prefix/foo' not in list(bucket.objects.all())


@moto.mock_s3
def test_delete_missing(task, valid_config):
    bucket = create_bucket()
    task.run(valid_config)
    assert 'prefix/foo' not in list(bucket.objects.all())
