import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

DATA_DIR = Path(os.environ.get('STUDYHUB_DATA_DIR') or (Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share')) / 'StudyHub'))
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / 'attachments').mkdir(exist_ok=True)
(DATA_DIR / 'backups').mkdir(exist_ok=True)
engine = create_engine(f"sqlite:///{(DATA_DIR / 'studyhub.db').as_posix()}", connect_args={'check_same_thread': False})
@event.listens_for(engine, 'connect')
def foreign_keys(dbapi_connection, _):
    dbapi_connection.execute('PRAGMA foreign_keys=ON')
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()
def get_db():
    with SessionLocal() as db:
        yield db
