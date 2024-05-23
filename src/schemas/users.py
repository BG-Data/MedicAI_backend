import mimetypes
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Union
from uuid import uuid4

import pytz
from fastapi import UploadFile
from pydantic import ConfigDict, EmailStr, Field, field_validator
from typing_extensions import Annotated

from common.class_exceptions import DocumentInvalid, PhotoInvalid
from schemas import LogRequestSchema, PydanticModel
from schemas.chats import ChatsHistorySchema, ChatsSchema
from settings import cfg
from utils import StringUtils

# Usuários
from utils.enums import UserType, UserTypePrivileged

tz = pytz.timezone("America/Sao_Paulo")


class UserBase(PydanticModel):
    "User Base Schema"
    email: EmailStr = Field(
        examples=["maria@medicai.com"],
        max_length=100,
    )
    name: str = Field(examples=["Maria Nogueira", "Leon Balloni"], max_length=255)
    password: str = Field(examples=[str(uuid4()), str(uuid4())], max_length=255)
    birthdate: date = Field(examples=[date(1995, 5, 25), date(1993, 3, 25)])
    document: str = Field(
        examples=["44.654.108/0001-73", "123.456.789-09"], max_length=18, min_length=11
    )
    document_type: Optional[str] = Field(examples=["CNPJ", "CPF", None], max_length=10)
    medical_document: Optional[str] = Field(examples=["192496", None], max_length=20)
    medical_document_type: Optional[str] = Field(examples=["CRM", None], max_length=18)
    deleted: bool = Field(examples=[True, False], default=False)
    privacy_terms: bool = Field(examples=[True, False])
    data_protection_terms: bool = Field(examples=[True, False])
    photo_object_name: Optional[str] = Field(
        default=None,
        examples=[
            "https://medic-ai.s3.us-west-1.amazonaws.com/photos/user_id%3A1/loen-removebg-preview.jpg"
        ],
        max_length=250,
    )

    @field_validator("document", mode="before")
    @classmethod
    def check_document(cls, document: str):
        if not document:
            raise DocumentInvalid(
                f"Documento inválido. O que foi encaminhado: {document}"
            )
        return StringUtils.remove_special_characters(document)

    @field_validator("document_type", mode="before")
    @classmethod
    def check_document_type(cls, document_type, values):
        if not document_type:
            return StringUtils.check_document_type_by_length(
                values.data.get("document")
            )


class UserSchema(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    user_type: UserType | UserTypePrivileged

    chat_history: Optional[List[ChatsHistorySchema]] = None
    logs: Optional[List[LogRequestSchema]] = None


class UserInsert(UserBase):
    user_type: UserType


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
