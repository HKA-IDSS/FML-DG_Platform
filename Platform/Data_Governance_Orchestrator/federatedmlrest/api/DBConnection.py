from pymongo.database import Database
from federatedmlrest.mongo import MongoDB
from minio import Minio

from federatedmlrest.minioS3 import MinioS3


def get_db() -> Database:
    """Get db object."""
    return MongoDB().db

def get_minio_s3() -> MinioS3:
    return MinioS3()