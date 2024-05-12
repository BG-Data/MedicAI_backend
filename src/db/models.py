from datetime import datetime

import pytz
from sqlalchemy import (
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
from sqlalchemy.orm import relationship

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


class UserModel(DefaultModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False, index=True, unique=True)
    photo_object = Column(
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


class Bots(DefaultModel):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    function = Column(String(100), nullable=True)


class ChatsHistory(DefaultModel):
    __tablename__ = "chats_history"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(1000), nullable=False)
    sender_id = Column(Integer, nullable=False)
    sender_type = Column(String(10), nullable=False)

    bot = relationship("Bots", foreign_keys=[sender_id])
    user = relationship("Users", foreign_keys=[sender_id])


class Chats(DefaultModel):
    id = Column(Integer, primary_key=True, index=True)
    chat_history_id = Column(Integer, ForeignKey("chats_history.id"), nullable=False)
    tag_group_id = Column(Integer, ForeignKey("tag_group.id"), nullable=False)
    file_object_name = Column(String(250), nullable=True)


class TagsGroups(DefaultModel):
    pass


class Tags(DefaultModel):
    pass
