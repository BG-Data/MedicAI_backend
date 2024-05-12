import sys
from datetime import datetime, timedelta
from typing import Annotated, Union

import pytz
from fastapi import APIRouter, Depends, HTTPException, Response, responses, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from loguru import logger
from sqlalchemy import or_

from common import DatabaseSessions, PasswordService
from db.connectors import Session, get_session
from db.models import Users
from settings import cfg

timezone = pytz.timezone("America/Sao_Paulo")
logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="Auth",
    level="INFO",
)


class AuthService(DatabaseSessions, PasswordService):
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

    def __db_check_user(self, username: str, password: str, session: Session) -> Users:
        """Checks if user exists"""
        user_query = (
            session.query(Users)
            .filter(or_(Users.email == username, Users.name == username))
            .one_or_none()
        )
        if not user_query:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Confere se a senha passada está correta
        if not self.get_password(password, user_query.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_query

    def __user_context(self, user_model: Users) -> dict:
        """What to be retrieved by frontend"""
        user_context = {
            "id": user_model.id,
            "name": user_model.name,
            "dt_created": str(user_model.created_at),
            "username": user_model.email,
            "type": user_model.user_type,
        }
        return user_context

    def generate_user_jwt(self, username: str, password: str, session: Session):
        # Confere se email/username está cadastrado
        user_query = self.__db_check_user(username, password, session)
        # Adiciona contexto para os dados do usuário (dados que podem ser úteis para front)
        user_context = self.__user_context(user_query)
        expire = datetime.utcnow() + timedelta(hours=int(cfg.JWT_ACCESS_TOKEN_EXPIRES))
        # Gerar token codificado
        encoded_jwt = jwt.encode(
            claims={"sub": username, "exp": expire, "context": user_context},
            key=cfg.SECRET_KEY,
            algorithm=cfg.ALGORITHM,
        )
        # retorno do jwt
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "user_context": user_context,
        }

    @staticmethod
    def get_auth_user_context(token: Annotated[str, Depends(oauth2_scheme)]):
        # Retorna o contexto do usuário
        try:
            payload = jwt.decode(token, cfg.SECRET_KEY, algorithms=[cfg.ALGORITHM])
            return payload
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials {exc}",
                headers={"WWW-Authenticate": "Bearer"},
            )


class AuthApi:
    def __init__(self):
        self.router = APIRouter()
        self.auth_service = AuthService()

        self.router.add_api_route(
            path="/auth", endpoint=self.login_for_access_token, methods=["POST"]
        )
        self.router.add_api_route(
            path="/user/session", endpoint=self.auth_health, methods=["GET"]
        )

    def login_for_access_token(
        self,
        auth_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: Session = Depends(get_session),
    ) -> Response:
        return responses.JSONResponse(
            self.auth_service.generate_user_jwt(
                username=auth_credentials.username,
                password=auth_credentials.password,
                session=session,
            ),
            200,
        )

    @staticmethod
    def auth_health(
        user_context: Annotated[dict, Depends(AuthService.get_auth_user_context)]
    ):
        return responses.JSONResponse(
            {
                "datetime": datetime.now(tz=timezone).strftime("%Y/%m/%d %H:%M:%S"),
                "status": "ok",
                "token expiration": datetime.fromtimestamp(
                    user_context.get("exp")
                ).strftime("%d/%m/%Y %H:%M"),
                "user_context": user_context.get("context"),
            },
            200,
        )
