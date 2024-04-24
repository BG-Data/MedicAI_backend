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
from db.models import UserModel
from db.schemas import UserInsert, UserSchema, UserUpdate

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="Api",
    level="INFO",
)


class UserApi(CrudApi):
    def __init__(
        self,
        model: UserModel = UserModel,
        schema: UserSchema = UserSchema,
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
            "/", self.insert, methods=["POST"], response_model=Union[schema, Any]
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
        self.service = UserService(model, schema)
        self.password_service = PasswordService()

    async def get(
        self,
        id: int = None,
        limit: int = 10,
        offset: int = 0,
        get_schema: Request = None,
        session: Session = Depends(get_session),
    ):
        try:
            user_data = await super().get(id, limit, offset, get_schema, session)
            return [user.model_dump(exclude={"password"}) for user in user_data]
        except Exception as exp:
            logger.error(f"error at get {self.__class__.__name__} {exp}")
            raise HTTPException(status_code=400, detail=str(exp))

    def insert(
        self, insert_schema: UserInsert, session: Session = Depends(get_session)
    ):
        "Ordinary user -> buyer"
        try:
            insert_schema.password = self.password_service.hash_password(
                insert_schema.password
            )
            return (
                super().insert(insert_schema, session).model_dump(exclude={"password"})
            )
        except Exception as exp:
            logger.error(f"error at insert {self.__class__.__name__} {exp}")

    def update(
        self,
        id: int,
        update_schema: MakeOptionalPydantic.make_partial_model(UserUpdate),
        session: Session = Depends(get_session),
    ):

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
        try:
            return self.crud.update_item(id, update_schema, session).model_dump(
                exclude={"password"}
            )
        except Exception as exp:
            logger.error(f"error at update {self.__class__.__name__} {exp}")
