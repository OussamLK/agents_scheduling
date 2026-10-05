from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import orjson
from src.types import Agent, AgentQualification, QualificationCode, Shift


class DB:
    @abstractmethod
    def get_qualified_agents(
        self, required_qualifications: list[QualificationCode]) -> list[Agent]: ...

    @abstractmethod
    def get_shift(self, shift_id) -> Optional[Shift]: ...

    @staticmethod
    @abstractmethod
    def from_json(path: str) -> DB: ...


@dataclass
class JsonDB(DB):
    agents: list[Agent]
    shifts: list[Shift]

    @staticmethod
    def from_json(path: str) -> DB:
        with open(path) as data_file:
            data = orjson.loads(data_file.read())
        return JsonDB(
            agents=[parse_db_agent(agent) for agent in data['agents']],
            shifts=[parse_db_shift(shift) for shift in data['shifts']])

    def get_shift(self, shift_id) -> Optional[Shift]:
        return next((s for s in self.shifts if s.id == shift_id), None)

    def get_qualified_agents(self, required_qualifications: list[QualificationCode]) -> list[Agent]:
        return [agent for agent in self.agents if self._agent_has_all_qualifications(agent, required_qualifications)]

    def _agent_has_all_qualifications(self, agent: Agent, required_qualifications: list[QualificationCode]) -> bool:
        agent_qual_codes = {q.code for q in agent.qualifications}
        required_codes = set(required_qualifications)
        return agent_qual_codes >= required_codes


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
