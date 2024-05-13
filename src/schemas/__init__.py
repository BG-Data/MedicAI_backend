import mimetypes
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Union
from uuid import uuid4

import pytz
from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import Annotated

from settings import cfg

# Usuários

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


class LogRequestSchema(PydanticModel):
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(200), nullable=False)
    method = Column(String(200), nullable=False)
    function_name = Column(String(200), nullable=False)
    status_code = Column(Integer, nullable=False)
    request = Column(JSON, nullable=True)
    comment = Column(String(200), nullable=True)
    latency = Column(Numeric(precision=14, scale=3), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    response = Column(JSON, nullable=True)
