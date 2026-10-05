from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import uuid

import orjson
from src.types import Agent, AgentQualification, Assignment, Interval, QualificationCode, Shift


class DB(ABC):
    @abstractmethod
    def get_qualified_agents(
        self, shift: Shift) -> list[Agent]: ...

    @abstractmethod
    def get_shift(self, shift_id) -> Optional[Shift]: ...

    @abstractmethod
    def get_agent(self, agent_id) -> Optional[Agent]: ...

    @staticmethod
    @abstractmethod
    def from_json(path: str) -> DB: ...

    def get_qualified_available_agents(self, shift_id: str) -> list[Agent]:
        ...

    def book_agent(self, agent: Agent, shift: Shift) -> Assignment: ...
    def agent_has_all_qualifications(
        self, agent: Agent, shift: Shift) -> bool: ...

    def agent_available(self, agent: Agent, shift: Shift) -> bool: ...
    def is_fully_booked(self, shift: Shift) -> bool: ...


@dataclass
class JsonDB(DB):
    agents: list[Agent]
    shifts: list[Shift]
    assignments: list[Assignment]
    _file_path: str

    @staticmethod
    def from_json(path: str) -> DB:
        with open(path) as data_file:
            data = orjson.loads(data_file.read())
        return JsonDB(
            agents=[parse_db_agent(agent) for agent in data['agents']],
            shifts=[parse_db_shift(shift) for shift in data['shifts']],
            assignments=[parse_db_assignment(a) for a in data['assignments']],
            _file_path=path
        )

    def get_shift(self, shift_id) -> Optional[Shift]:
        return next((s for s in self.shifts if s.id == shift_id), None)

    def get_agent(self, agent_id) -> Optional[Agent]:
        return next((a for a in self.agents if a.id == agent_id), None)

    def book_agent(self, agent: Agent, shift: Shift) -> Assignment:
        if not (self.agent_has_all_qualifications(agent, shift) and self.agent_available(agent, shift)):
            raise Exception(f'impossible to book agent to shift {shift.id}')
        return self._assign_agent(agent, shift)

    def is_fully_booked(self, shift: Shift) -> bool:
        return shift.headcount <= len(
            [a for a in self.assignments if a.shift_id == shift.id])

    def _assign_agent(self, agent: Agent, shift: Shift) -> Assignment:
        ...
        new_id = str(uuid.uuid4())
        assignment = Assignment(
            id=new_id, agent_id=agent.id, shift_id=shift.id)
        new_assignments = [assignment, * self.assignments]
        self._flush_assignments(new_assignments)
        return assignment

    def _flush_assignments(self, new_assignments: list[Assignment]) -> None:
        with open(self._file_path, 'r+') as f:
            data = orjson.loads(f.read())
            data['assignments'] = [
                serialize_assignment(a) for a in new_assignments]
            f.seek(0)
            f.write(orjson.dumps(data).decode())
            f.truncate()
            self.assignments = new_assignments

    def get_qualified_agents(self, shift: Shift) -> list[Agent]:
        return [agent for agent in self.agents if self.agent_has_all_qualifications(agent, shift)]

    def get_qualified_available_agents(self, shift_id: str) -> list[Agent]:
        shift = self.get_shift(shift_id)
        if shift is None:
            raise ValueError(
                f'checking availability for non existing shift {shift_id}')
        qualified = set(self.get_qualified_agents(shift))
        available = set(self._get_available_agents(shift))
        return list(qualified & available)

    def agent_has_all_qualifications(self, agent: Agent, shift: Shift) -> bool:
        agent_qual_codes = {
            q.code for q in agent.qualifications if q.expires_on >= shift.start}
        required_codes = set(shift.required_qualifications)
        return agent_qual_codes >= required_codes

    def _get_available_agents(self, shift: Shift) -> list[Agent]:
        return [agent for agent in self.agents if self.agent_available(agent, shift)]

    def agent_available(self, agent: Agent, shift: Shift) -> bool:
        return self._no_overlap((shift.start, shift.end), self._get_agent_bookings(agent.id))

    def _get_agent_bookings(self, agent_id) -> list[Interval]:
        booked_shift_ids = {
            a.shift_id for a in self.assignments if a.agent_id == agent_id}
        return [(s.start, s.end) for s in self.shifts if s.id in booked_shift_ids]

    def _no_overlap(self, interval: Interval, bookings: list[Interval]):
        return all((not self._intervals_overlap(interval, booking) for booking in bookings))

    def _intervals_overlap(self, i1: Interval, i2: Interval) -> bool:
        if i1[0] <= i2[0]:
            return i1[1] > i2[0]
        else:
            return i2[1] > i1[0]


def parse_db_agent(agent: dict) -> Agent:
    return Agent(
        id=agent['id'],
        name=agent['name'],
        qualifications=[parse_db_qualification(q) for q in agent['qualifications']])


def parse_db_qualification(q: dict) -> AgentQualification:
    return AgentQualification(code=q['code'], expires_on=q['expiresOn'])


def parse_db_shift(shift: dict) -> Shift:
    return Shift(
        id=shift['id'],
        site=shift['site'],
        start=shift['start'],
        end=shift['end'],
        required_qualifications=shift['requiredQualifications'],
        headcount=shift['headcount'])


def parse_db_assignment(assignment: dict) -> Assignment:
    return Assignment(
        id=assignment['id'],
        shift_id=assignment['shiftId'],
        agent_id=assignment['agentId'])


def serialize_assignment(assignment: Assignment) -> dict:
    return dict(id=assignment.id, shiftId=assignment.shift_id, agentId=assignment.agent_id)
