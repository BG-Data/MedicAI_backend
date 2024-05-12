import sys
from json import dumps
from typing import Any, Dict, List, Union
from uuid import uuid4

from fastapi import HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from loguru import logger

from app import UserService
from common import PasswordService
from common.auth import AuthService
from common.generic import CrudApi, Depends
from db import MakeOptionalPydantic
from db.connectors import Session, get_session
from db.models import Users
from schemas import UserInsert, UserSchema, UserUpdate

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="FLowise API",
    level="INFO",
)


class FlowiseApi(CrudApi):
    def __init__(
        self,
        model: FlowiseModel = FlowiseModel,
        schema: FlowiseSchema = FlowiseSchema,
        *args,
        **kwargs,
    ):
        super().__init__(model, schema, *args, **kwargs)
        self.add_api_route(
            "/",
            self.post,
            methods=["POST"],
            response_model=Union[List[schema], schema, Any],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
