import json

from typing import Optional

from pydantic import BaseModel, validator, Field


class _Responsible(BaseModel):
    id: Optional[str] = Field(alias='_id', omit_default=True)
    governance_id: str = Field(alias="_governance_id")
    version: Optional[str] = Field(alias='_version', omit_default=True)
    current: Optional[str] = Field(alias='_current', omit_default=True)
    name: Optional[str] = Field(omit_default=True)
    organisation_id: Optional[str] = Field(omit_default=True)
    description: Optional[str] = Field(omit_default=True)
    ip: Optional[str] = Field(omit_default=True)


class ActivityModel(BaseModel):
    """
    Model for activities
    """
    responsible: _Responsible
    name: str
    affected_objects: dict[str, str]
    start_time: str
    end_time: str

    @validator('affected_objects', pre=True)
    def parse_affected_objects(cls, value: str):
        """
        converts affected_objects back to a string
        :param value: affected_objects string
        :returns: json of affected_objects
        """
        if isinstance(value, str):
            return json.loads(value)
        return value
