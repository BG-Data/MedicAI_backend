from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from settings import cfg

# remove connect_args if using any other db than sqlite
engine = create_engine(url=cfg.DATABASE_URL)
# connect_args={"check_same_thread": Config.SQLALCHEMY_TRACK_MODIFICATIONS}
if not database_exists(engine.url):
    create_database(engine.url)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


Base = declarative_base()
