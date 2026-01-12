from pydantic import BaseModel


class EntityModel(BaseModel):
    """
    Model for entities
    """
    governance_id: str
    version: int
    timestamp: str
