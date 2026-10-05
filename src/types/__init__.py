import datetime
from typing import Annotated, Literal
from pydantic import AfterValidator, BaseModel


def _to_utc(dt: datetime.datetime) -> datetime.datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)
    return dt.astimezone(datetime.UTC)


type UTCDatetime = Annotated[datetime.datetime, AfterValidator(_to_utc)]
type QualificationCode = str
type Interval = tuple[UTCDatetime, UTCDatetime]


class AgentQualification(BaseModel):
    code: str
    expires_on: UTCDatetime


class Agent(BaseModel):
    id: str
    name: str
    qualifications: list[AgentQualification]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Agent):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class Shift(BaseModel):
    id: str
    site: str
    start: UTCDatetime
    end: UTCDatetime
    required_qualifications: list[QualificationCode]
    headcount: int


class Assignment(BaseModel):
    id: str
    shift_id: str
    agent_id: str
