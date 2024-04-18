import sys
from time import sleep
from typing import List

from fastapi import Depends, HTTPException, UploadFile, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, or_

from common import DatabaseSessions, get_current_method_name
from common.aws import AwsClient
from db.connectors import Base, Session, get_session
from db.models import UserModel
from settings import cfg

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="Services",
    level="INFO",
)


class UserService:
    def __init__(self, model: Base, schema: BaseModel):
        self.model = model
        self.base_schema = schema
