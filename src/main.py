import uvicorn

from base import init_app

# from settings import cfg


app, Base = init_app()

app_base_configs = {
    "host": "0.0.0.0",
    "port": 8001,  # int(cfg.PORT),
    "workers": 1,  # int(cfg.UVICORN_WORKERS),
    "access_log": True,
    "reload": True,  # bool(cfg.RELOAD)
}
if __name__ == "__main__":
    uvicorn.run("main:app", **app_base_configs)
