from collections.abc import Generator
from sqlmodel import Session
from app.core.init_db import engine


def get_core_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

