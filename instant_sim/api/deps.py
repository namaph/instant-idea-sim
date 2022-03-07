import logging
import uuid

from google.cloud import firestore
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.transforms import Sentinel


def get_uvicorn_logger() -> logging.Logger:
    return logging.getLogger("uvicorn")


def get_firestore() -> Client:
    return firestore.Client()


def get_servertime() -> Sentinel:
    return firestore.SERVER_TIMESTAMP


def get_uuid() -> str:
    return str(uuid.uuid4())
