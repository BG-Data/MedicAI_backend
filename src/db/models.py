from datetime import datetime
from typing import List

import pytz
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, foreign, relationship

from db.connectors import Base

# import datetime


class DefaultModel(Base):
    tz = pytz.timezone("America/Sao_Paulo")
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.now(tz=tz), index=True)
    updated_at = Column(
        DateTime, default=datetime.now(tz=tz), onupdate=datetime.now(tz=tz), index=True
    )

    def formatted_date_created(self):
        return func.to_char(self.created_at, "YYYY-MM-DD")

    def formatted_datetime_created(self):
        return func.to_char(self.created_at, "YYYY-MM-DD HH24:MI:SS")

    def formatted_time_created(self):
        return func.to_char(self.created_at, "HH24:MI:SS")

    def formatted_date_updated(self):
        return func.to_char(self.updated_at, "YYYY-MM-DD")

    def formatted_datetime_updated(self):
        return func.to_char(self.updated_at, "YYYY-MM-DD HH24:MI:SS")

    def formatted_time_updated(self):
        return func.to_char(self.updated_at, "HH24:MI:SS")


class Users(DefaultModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False, index=True, unique=True)
    photo_object_name = Column(
        String(250),
        nullable=True,
        comment="Representa o nome do objeto no bucket s3 e seu caminho",
    )
    birthdate = Column(Date, nullable=False, index=True)
    privacy_terms = Column(Boolean, nullable=False)
    data_protection_terms = Column(Boolean, nullable=False)
    document = Column(String(18), nullable=False, index=True, unique=True)
    document_type = Column(String(10), nullable=False)
    medical_document = Column(String(20), nullable=True, index=True)
    medical_document_type = Column(String(18), nullable=True, index=True, default="crm")
    user_type = Column(
        String(30), nullable=False, default="cliente"
    )  # comprador, administrador(apenas devs) e vendedor
    deleted = Column(
        Boolean, nullable=False, default=False
    )  # Usuário está desativado? (padrão é False) rmeoção lógica e não física

    chat_history: Mapped[List["ChatsHistory"]] = relationship(
        back_populates="user_history"
    )
    logs: Mapped[List["LogRequest"]] = relationship(back_populates="user_logs")
    chats: Mapped[List["Chats"]] = relationship(back_populates="user_chat")


class Bots(DefaultModel):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    function = Column(String(100), nullable=True)

    # chat_history: Mapped[List["ChatsHistory"]] = relationship(
    #     back_populates="bot_history"
    # )


# @TODO -> Solve the issue with Composite Foreign Key  https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#overlapping-foreign-keys

# @TODO -> Could be solved using UUID to avoid Collision or by simplying removing the relationship below.


class ChatsHistory(DefaultModel):
    __tablename__ = "chats_history"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    message = Column(String(10000), nullable=False)
    sender_id = Column(
        Integer,
        ForeignKey(
            "users.id",
        ),
        nullable=False,
    )
    sender_type = Column(String(10), nullable=False)

    # bot_history: Mapped[Bots] = relationship(
    #     foreign_keys=[sender_id], back_populates="chat_history", overlaps="user_history"
    # )
    user_history: Mapped[Users] = relationship(
        foreign_keys=[sender_id],
        back_populates="chat_history",
        overlaps="bot_history",
    )
    chat: Mapped["Chats"] = relationship(back_populates="chat_history")
    # __table_args__ = (
    #     ForeignKeyConstraint(
    #         ["sender_id"], ["bots.id"], onupdate="CASCADE", name="fk_bot_sender"
    #     ),
    #     ForeignKeyConstraint(
    #         ["sender_id"], ["users.id"], onupdate="CASCADE", name="fk_user_sender"
    #     ),
    # )


class TagGroups(DefaultModel):
    __tablename__ = "tag_groups"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)


class Chats(DefaultModel):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    file_object_name = Column(String(250), nullable=True)
    favority = Column(Boolean, nullable=True, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_history: Mapped[List[ChatsHistory]] = relationship(back_populates="chat")
    tags: Mapped[List["Tags"]] = relationship(
        secondary="tag_groups", back_populates="chats"
    )
    user_chat: Mapped["Users"] = relationship(back_populates="chats")


class Tags(DefaultModel):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    chats: Mapped[List[Chats]] = relationship(
        secondary="tag_groups", back_populates="tags"
    )


class LogRequest(DefaultModel):
    __tablename__ = "log_request"
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

    user_logs: Mapped[List[Users]] = relationship(back_populates="logs")
