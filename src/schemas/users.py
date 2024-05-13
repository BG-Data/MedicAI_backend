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
from schemas import LogRequestSchema, PydanticModel
from schemas.chats import ChatSchema, ChatsHistorySchema
from settings import cfg

# Usuários
from utils.enums import UserType, UserTypePrivileged

tz = pytz.timezone("America/Sao_Paulo")


class UserBase(PydanticModel):
    email: str
    photo_object_name: Optional[str] = None


class UserSchema(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    password: str
    birthdate: date
    document: str
    document_type: str
    medical_document: Optional[str] = None
    medical_document_type: Optional[str] = None
    user_type: UserType | UserTypePrivileged
    deleted: bool
    privacy_terms: bool
    data_protection_terms: bool

    chat_history: Optional[List[ChatsHistorySchema]] = None
    logs: Optional[List[LogRequestSchema]] = None


class UserInsert(UserBase):
    name: str
    password: str
    birthdate: date
    document: str
    document_type: str
    medical_document: Optional[str] = None
    medical_document_type: Optional[str] = None
    user_type: UserType
    deleted: bool = False
    privacy_terms: bool
    data_protection_terms: bool


class UserInsertAdmin(UserInsert):
    user_type: UserTypePrivileged


class UserUpdate(UserInsert):
    model_config = ConfigDict(extra="allow")

    old_password: str


class PhotoSchema(PydanticModel):
    user_id: int
    filename: Annotated[Optional[str], Field(validate_default=True)] = None
    content_type: str
    mimetype: Annotated[Optional[str], Field(validate_default=True)] = None
    file_path: Annotated[Optional[str], Field(validate_default=True)] = None
    photo_file: UploadFile
    uploaded_file: Optional[dict] = Field(
        default=None, description="Dictionary containing uploaded file to bucket at S3"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("filename", mode="before")
    @classmethod
    def check_name(cls, filename: str, values):
        if not filename:
            return f"{str(uuid4())[-12:-1]}.{values.data.get('content_type')}"
        return filename

    @field_validator("mimetype", mode="before")
    @classmethod
    def guess_extension_type(cls, mimetype: str, values):
        if not values.data.get("content_type").startswith("image/"):
            raise PhotoInvalid(
                f"Tipo inválida de foto. Utilizado: {values.data.get('content_type')}"
            )
        if not mimetype:
            return mimetypes.guess_extension(values.data.get("content_type"))

    @field_validator("file_path", mode="before")
    @classmethod
    def create_file_path(cls, file_path: str, values):
        if not file_path:
            file_path = f"{cfg.AWS_PHOTO_BUCKET_FOLDER}/user_id:{values.data.get('user_id')}/{values.data.get('filename')}"
            return file_path


class BotsSchema(PydanticModel):
    id: int
    name: str
    function: str
    chat_history: Optional[List[ChatsHistorySchema]] = None
