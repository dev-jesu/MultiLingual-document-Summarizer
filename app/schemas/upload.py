from typing import Optional
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """
    Response schema for document parsing endpoints.
    """
    filename: str = Field(..., description="Name of the uploaded document file")
    pages: Optional[int] = Field(
        default=None, 
        description="Number of pages in the document (applicable for PDF)"
    )
    text: str = Field(..., description="Extracted plain text content from the document")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "judgement.pdf",
                "pages": 18,
                "text": "IN THE COURT OF THE DISTRICT JUDGE AT CHENNAI..."
            }
        }
    }


class ErrorDetail(BaseModel):
    """
    Standardized error response schema.
    """
    detail: str = Field(..., description="Error message description")
