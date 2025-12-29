from collections.abc import Generator
from sqlmodel import Session

from app.core.init_db import engine

def get_vsphere_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        session.exec("SET search_path TO plugin_vsphere")
        yield session
