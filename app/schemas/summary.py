from typing import Optional
from pydantic import BaseModel, Field

class SummaryResponse(BaseModel):
    """
    Response schema for document summarization endpoints.
    """
    filename: str = Field(..., description="Name of the uploaded document file")
    pages: Optional[int] = Field(
        default=None, 
        description="Number of pages in the document (applicable for PDF)"
    )
    estimated_tokens: int = Field(..., description="Estimated number of tokens in the document text")
    chunks_processed: int = Field(..., description="Number of text chunks processed")
    gemini_requests: int = Field(..., description="Total number of API requests made to Gemini")
    processing_time_seconds: float = Field(..., description="Time taken to process and summarize in seconds")
    summary: str = Field(..., description="The final generated legal summary")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "judgement.pdf",
                "pages": 186,
                "estimated_tokens": 42350,
                "chunks_processed": 8,
                "gemini_requests": 9,
                "processing_time_seconds": 18.4,
                "summary": "This document is a judgment from the District Court..."
            }
        }
    }
