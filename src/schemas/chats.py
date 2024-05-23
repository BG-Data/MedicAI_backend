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

# from schemas.users import UserSchema
from utils.enums import SenterType

# Usuários

tz = pytz.timezone("America/Sao_Paulo")


class ChatsHistoryBase(PydanticModel):
    chat_id: int
    message: str = Field(max_length=1000)
    sender_id: int
    sender_type: SenterType = Field(max_length=10)


class ChatsHistorySchema(ChatsHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    bot_history: Optional[List["BotsSchema"]] = None
    # user_history: Optional[List[UserSchema]] = None
    chat: Optional["ChatsSchema"] = None


class ChatsHistoryInsert(ChatsHistoryBase):
    pass


class ChatsHistoryUpdate(ChatsHistoryInsert):
    pass


class ChatsBase(PydanticModel):
    file_object_name: Optional[str] = None
    favority: bool = False


class ChatsSchema(ChatsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    chat_history: Optional[List[ChatsHistorySchema]] = None
    tags: Optional[List["TagsSchema"]] = None


class ChatsInsert(ChatsBase):
    chat_id: Optional[int] = Field(
        default=None,
        description=" Se houver um chat ja criado, vincular ao histórico dele, se não criar um novo chat.",
    )
    message: str
    sender_id: int = Field(description="Quem mandou a mensagem")


class ChatsUpdate(ChatsBase):
    pass


class TagsBase(PydanticModel):
    pass


class TagsSchema(TagsBase):
    pass


class BotsSchema(PydanticModel):
    id: int
    name: str
    function: str
    chat_history: Optional[List[ChatsHistorySchema]] = None
