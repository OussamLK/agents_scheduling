from src.persistence.db import DB
from ..types import AgentQualification, Agent, QualificationCode


class AgentService:
    def __init__(self, db: DB):
        self.db = db

    def getQualifiedAgents(self, required_qualifications: list[QualificationCode]) -> list[Agent]:
        return self.db.get_qualified_agents(required_qualifications)
