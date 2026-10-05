from src.persistence.db import DB
from ..types import AgentQualification, Agent, Assignment, QualificationCode, Shift


class AgentService:
    def __init__(self, db: DB):
        self.db = db

    def getAvailableQualifiedAgents(self, shift_id: str) -> list[Agent]:
        return self.db.get_qualified_available_agents(shift_id)

    def book_agent(self, agent: Agent, shift: Shift) -> Assignment:
        unavailable = not (self.db.agent_has_all_qualifications(
            agent, shift) and self.db.agent_available(agent, shift))
        overbooking = self.db.is_fully_booked(shift)
        if (unavailable or overbooking):
            reason = 'overbooking' if overbooking else 'agent unassignable'
            raise AssignmentError(
                f'impossible to book agent to shift {shift.id}: {reason}')
        return self.db.book_agent(agent, shift)


class AssignmentError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
