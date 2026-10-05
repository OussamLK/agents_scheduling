from abc import ABC, abstractmethod
from src.types import Agent, AgentQualification


class DB:
    @abstractmethod
    def getAgentsByQualification(
        self, qualifications: list[AgentQualification]) -> list[Agent]: ...
