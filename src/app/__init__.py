import sys
from time import sleep
from typing import List

from fastapi import Depends, HTTPException, Request, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, or_

from common import PasswordService, get_current_method_name
from common.aws import AwsClient
from common.generic import CrudService
from db import MakeOptionalPydantic
from db.connectors import Base, Session, get_session
from db.schemas import PhotoSchema, UserInsert, UserSchema, UserUpdate
from settings import cfg

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="Services",
    level="INFO",
)


class UserService(CrudService):
    def __init__(self, model: Base, schema: BaseModel):
        self.model = model
        self.base_schema = schema
        self.password_service = PasswordService()
        self.crud = CrudService(model, schema)
        self.aws_client = AwsClient(
            "s3",
            cfg.AWS_ACCESS_PHOTO_BUCKET_KEY,
            cfg.AWS_ACCESS_PHOTO_BUCKET_SECRET_KEY,
            cfg.AWS_PHOTO_BUCKET_REGION,
        )

    # TODO generate photo presigned url
    async def get_presigned_url(
        self,
        user_data: List[UserSchema],
    ) -> List[UserSchema]:
        # user_data = [user for ]
        for user in user_data:
            presigned_url = self.aws_client.create_presigned_url(user)
            user.photo_path = presigned_url

        return user_data

    def update_password(
        self,
        update_schema: MakeOptionalPydantic.make_partial_model(UserUpdate),
        session: Session,
    ) -> UserUpdate:
        if update_schema.model_dump(exclude_unset=True).get("old_password"):
            valid = self.password_service.get_password(
                update_schema.old_password,
                self.crud.get_itens({"id": id}, session)[0].password,
            )
            update_schema.old_password = None
            update_schema.password = self.password_service.hash_password(
                update_schema.password
            )
            if not valid:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "status_code": status.HTTP_401_UNAUTHORIZED,
                        "info": "The given password is not valid",
                    },
                )
        return update_schema

    def hash_password(self, insert_schema: UserInsert) -> UserInsert:
        insert_schema.password = self.password_service.hash_password(
            insert_schema.password
        )
        return insert_schema

    async def insert_photo(self, photo_schema: PhotoSchema) -> str:
        pass
        # TODO working on service procedures
        self.insert_to_bucket()
        self.insert_photo_to_db()
        self.get_presigned_url()
        return presigned_url

    async def update_photo(self):
        pass
