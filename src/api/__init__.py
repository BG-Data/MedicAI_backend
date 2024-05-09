import sys
from json import dumps
from typing import Any, Dict, List, Union
from uuid import uuid4

from fastapi import HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from loguru import logger

from app import UserService
from common.auth import AuthService
from common.class_exceptions import AwsInsertionFailed, PhotoInvalid
from common.generic import CrudApi, Depends
from db import MakeOptionalPydantic
from db.connectors import Session, get_session
from db.models import UserModel
from db.schemas import PhotoSchema, UserInsert, UserSchema, UserUpdate

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
        self.add_api_route(
            "/photo",
            self.insert_photo,
            methods=["POST"],
            response_model=Union[schema, Any, Dict[str, str]],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
        self.add_api_route(
            "/photo",
            self.update_photo,
            methods=["PUT"],
            response_model=Union[schema, Any, Dict[str, str]],
            dependencies=[Depends(AuthService.get_auth_user_context)],
        )
        self.service = UserService(model, schema)

    async def get(
        self,
        id: int = None,
        limit: int = 10,
        offset: int = 0,
        get_schema: Request = None,
        session: Session = Depends(get_session),
    ):
        """
        Esta é uma rota de recuperação de dados de usuários.

        Requisição:
            - Id : identificador do usuário \n
            - limit: Quantos itens quer recuperar (se houver) \n
            - offset: A partir de qual ponto da lista vc quer começar \n
            - Outros parâmetros: Qualquer outro argumento que tenha no modelo de usuário pode ser pesquisado. \n
            -> http://0.0.0.0:8000/user?user_type=cliente

        Retorno:

        Lista[Padrão UserSchema]
        """
        try:
            user_data = await super().get(id, limit, offset, get_schema, session)
            user_data = await self.service.get_presigned_url(user_data)
            return [user.model_dump(exclude={"password"}) for user in user_data]
        except Exception as exp:
            logger.error(f"error at get {self.__class__.__name__} {exp}")
            raise HTTPException(status_code=400, detail=str(exp))

    def insert(
        self,
        insert_schema: UserInsert,
        request: Request,
        session: Session = Depends(get_session),
    ):
        "Ordinary user -> client"
        try:
            if request.headers.get("authorization"):
                # TODO -> add user admin permission to insert a new admin to the server.
                AuthService.get_auth_user_context(
                    request.headers.get("authorization").split(" ")[-1]
                ).get("context").get("type")
            insert_schema = self.service.hash_password(insert_schema.password)
            return (
                super().insert(insert_schema, session).model_dump(exclude={"password"})
            )
        except Exception as exp:
            logger.error(f"error at insert {self.__class__.__name__} {exp}")
            raise HTTPException(status_code=400, detail=str(exp))

    def update(
        self,
        id: int,
        update_schema: MakeOptionalPydantic.make_partial_model(UserUpdate),
        session: Session = Depends(get_session),
    ):
        update_schema = self.service.update_password(update_schema, session)
        try:
            return self.crud.update_item(id, update_schema, session).model_dump(
                exclude={"password"}
            )
        except Exception as exp:
            logger.error(f"error at update {self.__class__.__name__} {exp}")
            raise HTTPException(status_code=400, detail=str(exp))

    async def insert_photo(
        self,
        photo: UploadFile,
        user: dict = Depends(AuthService.get_auth_user_context),
        session: Session = Depends(get_session),
    ):
        try:
            photo_schema = PhotoSchema(
                user_id=user.get("context").get("id"),
                filename=photo.filename,
                content_type=photo.content_type,
                photo_file=photo,
            )
            await self.service.insert_photo(photo_schema=photo_schema)
        except AwsInsertionFailed as exp:
            logger.error(str(exp))
            raise HTTPException(status_code=400, detail=str(exp))
        except PhotoInvalid as exp:
            logger.error(str(exp))
            raise HTTPException(status_code=422, detail=str(exp))
        except Exception as exp:
            logger.error(f"error at insert photo {self.__class__.__name__} {exp}")
            raise HTTPException(status_code=500, detail=str(exp))

    async def update_photo(
        self,
        photo: UploadFile,
        user_context: dict = Depends(AuthService.get_auth_user_context),
        session: Session = Depends(get_session),
    ):
        pass
