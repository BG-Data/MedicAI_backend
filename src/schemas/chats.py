import mimetypes
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Union
from uuid import uuid4

import pytz
from fastapi import UploadFile
from pydantic import ConfigDict, Field, field_validator
from typing_extensions import Annotated

from common.class_exceptions import PhotoInvalid
from schemas import PydanticModel
from settings import cfg

# Usuários
from utils.enums import UserType, UserTypePrivileged

tz = pytz.timezone("America/Sao_Paulo")


class ChatsHistoryBase(PydanticModel):
    pass


class ChatsHistorySchema(ChatsHistoryBase):
    pass


class ChatsBase(PydanticModel):
    pass


class ChatsSchema(ChatsBase):
    pass


class TagsBase(PydanticModel):
    pass


class TagsSchema(TagsBase):
    pass
