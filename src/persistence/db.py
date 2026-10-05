from abc import ABC, abstractmethod
from dataclasses import dataclass

import orjson
from src.types import Agent, AgentQualification


class DB:
    @abstractmethod
    def getQualifiedAgents(
        self, qualifications: list[AgentQualification]) -> list[Agent]: ...

    @staticmethod
    @abstractmethod
    def from_json(path: str) -> DB: ...


@dataclass
class JsonDB(DB):
    agents: list[Agent]

    @staticmethod
    def from_json(path: str) -> DB:
        with open(path) as data_file:
            data = orjson.loads(data_file.read())
        return JsonDB(agents=[parse_db_agent(agent) for agent in data['agents']])

    def getQualifiedAgents(self, qualifications: list[AgentQualification]) -> list[Agent]:
        return self.agents


def parse_db_agent(agent: dict) -> Agent:
    return Agent(
        id=agent['id'],
        name=agent['name'],
        qualifications=[parse_db_qualification(q) for q in agent['qualifications']])


def parse_db_qualification(q: dict) -> AgentQualification:
    return AgentQualification(code=q['code'], expires_on=q['expiresOn'])
