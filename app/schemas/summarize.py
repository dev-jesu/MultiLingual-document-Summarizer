from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """
    Response schema for legal document summarization endpoint.
    """
    filename: str = Field(..., description="Name of the uploaded document file")
    pages: int = Field(..., description="Number of pages or structural sections processed")
    estimated_tokens: int = Field(..., description="Total estimated token count of raw text")
    chunks_processed: int = Field(..., description="Total number of text chunks created")
    gemini_requests: int = Field(..., description="Total Gemini API requests executed")
    processing_time_seconds: float = Field(..., description="Total processing time in seconds")
    summary: str = Field(..., description="Extracted legal document summary")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "judgement.pdf",
                "pages": 18,
                "estimated_tokens": 12450,
                "chunks_processed": 3,
                "gemini_requests": 4,
                "processing_time_seconds": 8.45,
                "summary": "IN THE HIGH COURT OF JUDICATURE...\nKey Issues: ...\nFinal Judgment: Appeal dismissed."
            }
        }
    }
