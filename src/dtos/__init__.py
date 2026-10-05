from pydantic import BaseModel


class AgentDto(BaseModel):
    agentId: str
