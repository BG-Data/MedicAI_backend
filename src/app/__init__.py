import sys
from time import sleep
from typing import List

from fastapi import Depends, HTTPException, Request, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, or_

from common import FileProcessing, PasswordService, get_current_method_name
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
        super().__init__(model, schema)
        self.model = model
        self.base_schema = schema
        self.password_service = PasswordService()
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
        for i, user in enumerate(user_data):
            presigned_url = self.aws_client.create_presigned_url(
                cfg.AWS_BUCKET_NAME, user.photo_object, 600
            )
            user_data[i].photo_url = presigned_url

        return user_data

    def update_password(
        self,
        update_schema: MakeOptionalPydantic.make_partial_model(UserUpdate),
        session: Session,
    ) -> UserUpdate:
        if update_schema.model_dump(exclude_unset=True).get("old_password"):
            valid = self.password_service.get_password(
                update_schema.old_password,
                self.get_itens({"id": id}, session)[0].password,
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

    async def _insert_to_bucket(self, photo_schema: PhotoSchema):
        await FileProcessing.read_write_new_file(
            photo_schema.photo_file, photo_schema.filename
        )
        photo_schema.uploaded_file = self.aws_client.upload_file(
            photo_schema.filename, cfg.AWS_BUCKET_NAME, photo_schema.file_path, False
        )
        return photo_schema

    async def insert_photo(self, photo_schema: PhotoSchema, session: Session) -> str:
        users: List[UserSchema] = await self.get_itens(
            {"id": photo_schema.user_id}, session
        )
        if users[0].photo_object:
            self.aws_client.delete_file(cfg.AWS_BUCKET_NAME, users[0].photo_object)
        photo_schema = await self._insert_to_bucket(photo_schema)
        user_update = MakeOptionalPydantic.make_partial_model(UserUpdate)
        user_update = user_update(photo_object=photo_schema.file_path)
        users = self.update_item(
            photo_schema.user_id,
            user_update,
            session,
        )
        users = await self.get_presigned_url([users])
        return users
