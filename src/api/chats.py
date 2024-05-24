import sys
from json import dumps
from typing import Any, Dict, List, Union
from uuid import uuid4

from fastapi import HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from loguru import logger

from app.chats import ChatsService
from common.auth import AuthService
from common.class_exceptions import AwsInsertionFailed, PhotoInvalid, UserNotFound
from common.generic import CrudApi, Depends
from db import MakeOptionalPydantic
from db.connectors import Session, get_session
from db.models import Chats, ChatsHistory
from schemas.chats import (
    ChatMessageInsert,
    ChatsHistoryInsert,
    ChatsHistorySchema,
    ChatsHistoryUpdate,
    ChatsInsert,
    ChatsSchema,
    ChatsUpdate,
)

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="chats api",
    level="INFO",
)


class ChatsApi(CrudApi):
    api_name = "chats"
    router = "ChatsApi"
    tags = ["Chats"]
    prefix = "/chats"

    def __init__(
        self,
        model: Chats = Chats,
        schema: ChatsSchema = ChatsSchema,
        *args,
        **kwargs,
    ):
        super().__init__(model, schema, *args, **kwargs)
        self.add_api_route(
            "/",
            self.get,
            methods=["GET"],
            response_model=Union[List[schema], schema, Any],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
        self.add_api_route(
            "/",
            self.insert,
            methods=["POST"],
            response_model=Union[schema, ChatsHistorySchema, Any],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
        self.add_api_route(
            "/",
            self.update,
            methods=["PUT"],
            response_model=Union[schema, Any],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
        self.add_api_route(
            "/",
            self.delete,
            methods=["DELETE"],
            response_model=Union[schema, Any, Dict[str, str]],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
        self.chat_service = ChatsService(model, schema)

    async def insert(
        self,
        insert_schema: ChatMessageInsert,
        session: Session = Depends(get_session),
    ):
        try:
            result = await self.chat_service.insert(insert_schema, session)
            return result
        except Exception as exp:
            logger.error(f"error at {self.__class__.__name__} {exp}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp)
            )

    def update(
        self,
        insert_schema: ChatsUpdate,
        session: Session = Depends(get_session),
    ):
        try:
            return super().update(insert_schema, session).model_dump()
        except Exception as exp:
            logger.error(f"error at {self.__class__.__name__} {exp}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp)
            )


class ChatsHistoryApi(CrudApi):
    api_name = "chats_history"
    router = "ChatsHistoryApi"
    tags = ["Chats"]
    prefix = "/chats/history"

    def __init__(
        self,
        model: ChatsHistory = ChatsHistory,
        schema: ChatsHistorySchema = ChatsHistorySchema,
        *args,
        **kwargs,
    ):
        super().__init__(model, schema, *args, **kwargs)
        self.add_api_route(
            "/",
            self.get,
            methods=["GET"],
            response_model=Union[List[schema], schema, Any],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
        self.add_api_route(
            "/",
            self.update,
            methods=["PUT"],
            response_model=Union[schema, Any],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
        self.add_api_route(
            "/",
            self.delete,
            methods=["DELETE"],
            response_model=Union[schema, Any, Dict[str, str]],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )

    def update(
        self,
        insert_schema: ChatsHistoryUpdate,
        session: Session = Depends(get_session),
    ):
        try:
            return super().update(insert_schema, session).model_dump()
        except Exception as exp:
            logger.error(f"error at {self.__class__.__name__} {exp}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp)
            )
