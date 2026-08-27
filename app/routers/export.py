from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse, Response

from app.schemas.export import ExportRequest
from app.schemas.upload import ErrorDetail
from app.services.export_service import ExportService
from app.utils.logger import logger

router = APIRouter(prefix="/export", tags=["Report Export"])


def _generate_download_filename(filename: str, extension: str) -> str:
    """Generate dynamic filename like 'judgement_summary.pdf'."""
    clean_name = Path(filename).stem if filename else "document"
    clean_name = clean_name.replace(" ", "_")
    return f"{clean_name}_summary.{extension}"


@router.post(
    "/pdf",
    status_code=status.HTTP_200_OK,
    summary="Export legal summary as PDF",
    description="Generates and streams a professionally formatted PDF report for the provided summary.",
    responses={
        400: {"model": ErrorDetail, "description": "Invalid input or empty summary"},
        500: {"model": ErrorDetail, "description": "PDF generation error"}
    }
)
async def export_pdf(payload: ExportRequest):
    """Generate dynamic PDF report."""
    if not payload.summary or not payload.summary.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Summary text cannot be empty."
        )

    download_filename = _generate_download_filename(payload.filename, "pdf")
    logger.info("Export started | format=PDF | file=%s | time=%s", download_filename, payload.processing_time)

    try:
        pdf_buffer = ExportService.export_pdf(
            filename=payload.filename,
            summary=payload.summary,
            language=payload.language,
            processing_time=payload.processing_time
        )
        logger.info("Export completed | format=PDF | file=%s", download_filename)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
        )
    except Exception as exc:
        logger.error("Export failed | format=PDF | file=%s | error=%s", payload.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF export: {str(exc)}"
        ) from exc


@router.post(
    "/docx",
    status_code=status.HTTP_200_OK,
    summary="Export legal summary as DOCX",
    description="Generates and streams a professionally formatted Word DOCX report for the provided summary.",
    responses={
        400: {"model": ErrorDetail, "description": "Invalid input or empty summary"},
        500: {"model": ErrorDetail, "description": "DOCX generation error"}
    }
)
async def export_docx(payload: ExportRequest):
    """Generate dynamic DOCX report."""
    if not payload.summary or not payload.summary.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Summary text cannot be empty."
        )

    download_filename = _generate_download_filename(payload.filename, "docx")
    logger.info("Export started | format=DOCX | file=%s | time=%s", download_filename, payload.processing_time)

    try:
        docx_buffer = ExportService.export_docx(
            filename=payload.filename,
            summary=payload.summary,
            language=payload.language,
            processing_time=payload.processing_time
        )
        logger.info("Export completed | format=DOCX | file=%s", download_filename)
        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
        )
    except Exception as exc:
        logger.error("Export failed | format=DOCX | file=%s | error=%s", payload.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DOCX export: {str(exc)}"
        ) from exc


@router.post(
    "/txt",
    status_code=status.HTTP_200_OK,
    summary="Export legal summary as TXT",
    description="Generates and streams a UTF-8 encoded plain text report for the provided summary.",
    responses={
        400: {"model": ErrorDetail, "description": "Invalid input or empty summary"},
        500: {"model": ErrorDetail, "description": "TXT generation error"}
    }
)
async def export_txt(payload: ExportRequest):
    """Generate dynamic TXT report."""
    if not payload.summary or not payload.summary.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Summary text cannot be empty."
        )

    download_filename = _generate_download_filename(payload.filename, "txt")
    logger.info("Export started | format=TXT | file=%s | time=%s", download_filename, payload.processing_time)

    try:
        txt_bytes = ExportService.export_txt(
            filename=payload.filename,
            summary=payload.summary,
            language=payload.language,
            processing_time=payload.processing_time
        )
        logger.info("Export completed | format=TXT | file=%s", download_filename)
        return Response(
            content=txt_bytes,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
        )
    except Exception as exc:
        logger.error("Export failed | format=TXT | file=%s | error=%s", payload.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate TXT export: {str(exc)}"
        ) from exc
