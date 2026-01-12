from pydantic import BaseModel


class AgentModel(BaseModel):
    """
    Model for agents
    """
    governance_id: str
    version: int
    timestamp: str
