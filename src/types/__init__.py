import datetime
from typing import Literal
from pydantic import BaseModel


class AgentQualification(BaseModel):
    code: str
    expires_on: datetime.datetime


class Agent(BaseModel):
    id: str
    name: str
    qualifications: list[AgentQualification]


class Shift(BaseModel):
    id: str
    site: str
    start: datetime.datetime
    end: datetime.datetime
    required_qualifications: list[AgentQualification]
    headcount: int


class Assignment(BaseModel):
    id: str
    shift_id: str
    agent_id: str
