from src.persistence.db import DB
from ..types import AgentQualification, Agent


class AgentService:
    def __init__(self, db: DB):
        self.db = db

    def getQualifiedAgents(self, required_qualifications: list[AgentQualification]) -> list[Agent]:
        return self.db.getQualifiedAgents(required_qualifications)
