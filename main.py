from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from src.persistence import DBDeps
from src.types import AgentQualification, QualificationCode

app = FastAPI()


@app.get('/agents')
def get_agents(db: DBDeps):
    return db.get_qualified_agents([])


@app.get('/api/shifts/{shift_id}/available-agents')
def get_available_agents(
        shift_id: str,
        db: DBDeps):
    shift = db.get_shift(shift_id)
    if shift is None:
        raise HTTPException(
            status_code=404, detail=f"Shift '{shift_id}' not found")
    return db.get_qualified_agents(shift.required_qualifications)
