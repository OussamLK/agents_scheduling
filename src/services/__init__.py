from src.persistence.db import DB
from ..types import AgentQualification, Agent, QualificationCode


class AgentService:
    def __init__(self, db: DB):
        self.db = db

    def getAvailableQualifiedAgents(self, shift_id: str) -> list[Agent]:
        return self.db.get_qualified_available_agents(shift_id)
