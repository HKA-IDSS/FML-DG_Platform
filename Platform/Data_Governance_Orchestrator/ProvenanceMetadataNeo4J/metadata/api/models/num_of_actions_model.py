from typing import Optional

from pydantic import BaseModel, Field


class _Responsible(BaseModel):
    id: Optional[str] = Field(alias='_id', omit_default=True)
    governance_id: str = Field(alias="_governance_id")
    version: Optional[str] = Field(alias='_version', omit_default=True)
    current: Optional[str] = Field(alias='_current', omit_default=True)
    name: Optional[str] = Field(omit_default=True)
    organisation_id: Optional[str] = Field(omit_default=True)
    description: Optional[str] = Field(omit_default=True)
    ip: Optional[str] = Field(omit_default=True)


class NumOfActionModel(BaseModel):
    """
    Model for number of activities
    """
    responsible: _Responsible
    num_of_actions: int
