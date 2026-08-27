from typing import Optional
from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    """
    Input schema for document summary export requests.
    """
    filename: str = Field(
        ...,
        description="Original name of the document file (e.g., 'judgement.pdf')",
        examples=["judgement.pdf"]
    )
    summary: str = Field(
        ...,
        min_length=1,
        description="The AI-generated legal summary text to be exported",
        examples=["IN THE HIGH COURT OF JUDICATURE...\nKey Issues: ..."]
    )
    language: Optional[str] = Field(
        default="en",
        description="Language code or name of the summary content (e.g. 'ta', 'Tamil', 'hi', 'en')",
        examples=["ta"]
    )
    processing_time: Optional[str] = Field(
        default="N/A",
        description="Execution processing time string (e.g. '18.4s')",
        examples=["18.4s"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "judgement.pdf",
                "summary": "IN THE HIGH COURT OF JUDICATURE AT MADRAS\n\n1. Facts of the Case...\n2. Legal Issues...",
                "language": "ta",
                "processing_time": "18.4s"
            }
        }
    }
