import sys

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.chats import ChatsApi, ChatsHistoryApi
from api.users import UserApi
from common.auth import AuthApi
from common.base_users import BaseUsers
from db.connectors import Base, engine
from schemas import Health

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="Init api",
    level="INFO",
)


def init_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


def init_app():
    app = FastAPI()
    api_routes = {
        "users": {"router": UserApi(), "tags": ["Usuarios"], "prefix": "/users"},
        "chats": {"router": ChatsApi(), "tags": ["Chats"], "prefix": "/chats"},
        "chats_history": {
            "router": ChatsHistoryApi(),
            "tags": ["Chats"],
            "prefix": "/chats/history",
        },
    }
    app = init_middlewares(app)
    app = init_auth(app)
    app = init_routes(app, api_routes)
    Base.metadata.create_all(bind=engine)
    # base_users = BaseUsers().create_base_users()
    # logger.info(base_users)
    return app, Base


def init_routes(app: FastAPI, api_routes: dict):

    @app.get("/", response_model=Health, status_code=200)
    def status_api():
        return Health().model_dump()

    for route_key in api_routes.keys():
        app.include_router(**api_routes.get(route_key))
    return app


def init_auth(app: FastAPI):
    app.include_router(
        AuthApi().router,
        tags=["Auth"],
    )
    return app
