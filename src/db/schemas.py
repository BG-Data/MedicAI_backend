from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict

from settings import cfg

# Usuários
from utils.enums import UserType, UserTypePrivileged


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
    datetime: str = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")
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
    lgpd: bool
    document: str
    document_type: str
    user_type: UserType | UserTypePrivileged
    deleted: bool


class UserInsert(UserBase):
    name: str
    password: str
    birthdate: date
    lgpd: bool
    document: str
    document_type: str
    user_type: UserType
    deleted: bool = False


class UserInsertAdmin(UserBase):
    name: str
    password: str
    birthdate: date
    lgpd: bool
    document: str
    document_type: str
    user_type: UserTypePrivileged
    deleted: bool = False


class UserUpdate(UserInsert):
    old_password: str
