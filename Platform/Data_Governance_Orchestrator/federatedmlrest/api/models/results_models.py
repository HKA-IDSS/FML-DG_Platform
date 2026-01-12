"""Models for results endpoints."""

from pydantic import BaseModel, Field
from typing import Literal


class FileUploadResponse(BaseModel):
    """Response model for file upload operations."""
    message: str = Field(description="Success message")
    filename: str = Field(description="Name of the uploaded file")
    governance_id: str = Field(alias="_governance_id", description="Governance ID of the configuration")
    file_type: Literal["evaluation_results", "trained_model"] = Field(description="Type of uploaded file")

    class Config:
        """Pydantic config."""
        populate_by_name = True