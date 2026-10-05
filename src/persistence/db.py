from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import orjson
from src.types import Agent, AgentQualification, Assignment, Interval, QualificationCode, Shift


class DB:
    @abstractmethod
    def get_qualified_agents(
        self, shift: Shift) -> list[Agent]: ...

    @abstractmethod
    def get_shift(self, shift_id) -> Optional[Shift]: ...

    @staticmethod
    @abstractmethod
    def from_json(path: str) -> DB: ...

    def get_qualified_available_agents(self, shift_id: str) -> list[Agent]:
        ...


@dataclass
class JsonDB(DB):
    agents: list[Agent]
    shifts: list[Shift]
    assignments: list[Assignment]

    @staticmethod
    def from_json(path: str) -> DB:
        with open(path) as data_file:
            data = orjson.loads(data_file.read())
        return JsonDB(
            agents=[parse_db_agent(agent) for agent in data['agents']],
            shifts=[parse_db_shift(shift) for shift in data['shifts']],
            assignments=[parse_db_assignment(a) for a in data['assignments']])

    def get_shift(self, shift_id) -> Optional[Shift]:
        return next((s for s in self.shifts if s.id == shift_id), None)

    def get_qualified_agents(self, shift: Shift) -> list[Agent]:
        return [agent for agent in self.agents if self._agent_has_all_qualifications(agent, shift)]

    def get_qualified_available_agents(self, shift_id: str) -> list[Agent]:
        shift = self.get_shift(shift_id)
        if shift is None:
            raise ValueError(
                f'checking availability for non existing shift {shift_id}')
        qualified = set(self.get_qualified_agents(shift))
        available = set(self._get_available_agents(shift))
        return list(qualified & available)

    def _agent_has_all_qualifications(self, agent: Agent, shift: Shift) -> bool:
        agent_qual_codes = {
            q.code for q in agent.qualifications if q.expires_on >= shift.start}
        required_codes = set(shift.required_qualifications)
        return agent_qual_codes >= required_codes

    def _get_available_agents(self, shift: Shift) -> list[Agent]:
        return [agent for agent in self.agents if self._agent_available(agent.id, shift)]

    def _agent_available(self, agent_id, shift: Shift) -> bool:
        return self._no_overlap((shift.start, shift.end), self._get_agent_bookings(agent_id))

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
