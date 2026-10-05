from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from src.dtos import AgentDto
from src.persistence import DBDeps
from src.services import AgentService, AssignmentError
from src.types import AgentQualification, QualificationCode

app = FastAPI()


@app.get('/api/shifts/{shift_id}/available-agents')
def get_available_agents(
        shift_id: str,
        db: DBDeps):
    shift = db.get_shift(shift_id)
    if shift is None:
        raise HTTPException(
            status_code=404, detail=f"Shift '{shift_id}' not found")
    return db.get_qualified_available_agents(shift_id)


@app.post('/api/shifts/{shift_id}/assignments')
def create_assignment(shift_id: str, agent: AgentDto, db: DBDeps):
    agent_service = AgentService(db)
    shift = db.get_shift(shift_id)
    if shift is None:
        raise HTTPException(
            status_code=404, detail=f"Shift '{shift_id}' not found")
    db_agent = db.get_agent(agent.agentId)
    if db_agent is None:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent.agentId}' not found")
    try:
        assignment = agent_service.book_agent(db_agent, shift)
    except AssignmentError:
        raise HTTPException(
            status_code=404, detail=f"Can not book '{agent.agentId}' on shift {shift.id}")
    # write error will just crash this and return 500
    return assignment
