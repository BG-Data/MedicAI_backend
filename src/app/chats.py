import sys
from time import sleep
from typing import List, Tuple

from fastapi import Depends, HTTPException, Request, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, or_

from api.flowise import FlowiseApi
from common import FileProcessing, PasswordService, get_current_method_name
from common.aws import AwsClient
from common.generic import CrudService
from db import MakeOptionalPydantic
from db.connectors import Base, Session, get_session
from db.models import ChatsHistory
from domain.chats import ChatsDomain
from schemas.chats import (
    ChatMessageInsert,
    ChatsHistoryInsert,
    ChatsHistorySchema,
    ChatsInsert,
    ChatsSchema,
)
from settings import cfg
from utils.enums import SenderType

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="Services",
    level="INFO",
)


class ChatsService(CrudService):
    flowise = FlowiseApi()

    def __init__(self, model: Base, schema: BaseModel):
        super().__init__(model, schema)
        self.model = model
        self.base_schema = schema
        self.chat_domain = ChatsDomain()
        self.chat_history_service = ChatsHistoryService(
            ChatsHistory, ChatsHistorySchema
        )

    def _prepare_chat_history_data(self, insert_schema: ChatMessageInsert):
        pass

    async def insert(
        self, insert_schema: ChatMessageInsert, session
    ) -> Tuple[ChatsSchema, ChatsHistorySchema]:
        new_chat = None
        if not insert_schema.chat_id:
            new_chat = self._insert_new_chat(insert_schema, session)
            insert_schema.chat_id = new_chat.id
        insert_new_message = ChatsHistoryInsert(
            chat_id=insert_schema.chat_id,
            message=insert_schema.message,
            sender_id=insert_schema.user_id,
            sender_type=SenderType.usuario,
        )
        self._insert_new_message(insert_new_message, session)
        try:
            self._insert_bot_message(insert_schema, session)
        except Exception as exp:
            None
        if not new_chat:
            new_chat = await self.get_itens(
                {"id": insert_schema.chat_id, "limit": 1000}, session
            )
            new_chat = new_chat[0]
        return new_chat

    def _get_bot_answer(self, question: str) -> str:
        return self.flowise.ask_bot(question)

    def _insert_bot_message(self, insert_schema: ChatMessageInsert, session) -> None:
        bot_msg = self._get_bot_answer(insert_schema.message)
        insert_new_message = ChatsHistoryInsert(
            chat_id=insert_schema.chat_id,
            message=bot_msg,
            sender_id=insert_schema.user_id,
            sender_type=SenderType.bot,
        )
        self._insert_new_message(insert_new_message, session)

    def _insert_new_chat(self, insert_schema: ChatMessageInsert, session: Session):
        logger.info("Creating New Chat")
        new_chat = ChatsInsert(
            file_object_name=insert_schema.file_object_name,
            favority=insert_schema.favority,
            user_id=insert_schema.user_id,
        )
        return self.insert_item(
            new_chat,
            session,
        )

    def _insert_new_message(self, insert_schema: ChatsHistoryInsert, session: Session):
        logger.info(f"Handling chat {insert_schema.chat_id}")
        return self.chat_history_service.insert_item(insert_schema, session)

    def check_chat_message(self, insert_schema: ChatMessageInsert) -> callable:
        callable_method = getattr(
            self, self.chat_domain.check_message_content(insert_schema), None
        )
        if not callable_method:
            ValueError("Atributo de insert chat não existente")
        return callable_method


class ChatsHistoryService(CrudService):
    def __init__(self, model: Base, schema: BaseModel):
        super().__init__(model, schema)
        self.model = model
        self.base_schema = schema
