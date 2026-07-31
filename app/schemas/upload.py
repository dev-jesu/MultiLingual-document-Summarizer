from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChunkDetail(BaseModel):
    """
    Schema representing a single text chunk.
    """
    chunk_index: int = Field(..., description="0-indexed position of chunk in document sequence")
    text: str = Field(..., description="Text content of the chunk")
    token_estimate: int = Field(..., description="Estimated token count for this chunk")


class DocumentResponse(BaseModel):
    """
    Response schema for document parsing and chunking endpoints.
    """
    filename: str = Field(..., description="Name of the uploaded document file")
    pages: Optional[int] = Field(
        default=None, 
        description="Number of pages in the document (applicable for PDF)"
    )
    text: str = Field(..., description="Extracted raw text content")
    cleaned_text: str = Field(..., description="Cleaned and normalized text content")
    strategy_used: str = Field(..., description="Chunking strategy applied")
    total_chunks: int = Field(..., description="Total number of chunks produced")
    chunks: list[ChunkDetail] = Field(default_factory=list, description="List of document chunks")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "judgement.pdf",
                "pages": 18,
                "text": "IN THE COURT OF THE DISTRICT JUDGE...",
                "cleaned_text": "IN THE COURT OF THE DISTRICT JUDGE...",
                "strategy_used": "paragraph",
                "total_chunks": 4,
                "chunks": [
                    {
                        "chunk_index": 0,
                        "text": "IN THE COURT OF THE DISTRICT JUDGE AT CHENNAI...",
                        "token_estimate": 150
                    }
                ]
            }
        }
    }


class ErrorDetail(BaseModel):
    """
    Standardized error response schema.
    """
    detail: str = Field(..., description="Error message description")
