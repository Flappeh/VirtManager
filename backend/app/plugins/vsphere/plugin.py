from typing import Iterable
from sqlalchemy import MetaData
from fastapi import APIRouter

class Plugin:
    name: str
    version: str
    description: str
    def register_metadata(self) -> Iterable[MetaData]:
        ...

    def register_routers(self) -> Iterable[APIRouter]:
        ...
