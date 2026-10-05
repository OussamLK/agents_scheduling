from pathlib import Path
from typing import Annotated

from fastapi import Depends

from .db import DB, JsonDB

DATA_PATH = Path(__file__).resolve().parent / "data.json"
json_db = JsonDB.from_json(str(DATA_PATH))


def get_db():
    yield json_db


type DBDeps = Annotated[DB, Depends(get_db)]
