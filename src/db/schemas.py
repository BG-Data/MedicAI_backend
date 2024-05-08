from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Union
from uuid import uuid4

import pytz
from pydantic import BaseModel, ConfigDict, Field, field_validator

from settings import cfg

# Usuários
from utils.enums import UserType, UserTypePrivileged

tz = pytz.timezone("America/Sao_Paulo")


class PydanticModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # @validator('*', pre=True)
    # def format_date_fields(cls, v):
    #     if isinstance(v, date):
    #         return v.strftime('%d-%m-%Y')
    #     elif isinstance(v, datetime):
    #         return v.strftime('%d-%m-%Y %H:%M:%S')
    #     return v


class Health(PydanticModel):

    datetime: str = datetime.now(tz=tz).strftime("%d-%m-%Y %H:%M:%S")
    status: str = "ok"
    environment: str = cfg.ENVIRONMENT


class UserBase(PydanticModel):
    email: str


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
    old_password: str


class PhotoSchema:
    user_id: str
    filename: str
    content_type: str
    file_path: str
    photo_name: Optional[str] = Field(default_factory=uuid4)

    @field_validator(field="photo_name", mode="before")
    @classmethod
    def convert_uuid(cls, photo_name: str):
        if photo_name:
            return str(photo_name)
