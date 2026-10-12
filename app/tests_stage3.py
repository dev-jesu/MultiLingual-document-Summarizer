"""
Stage 3 Tests: Gemini LLM Summarization Pipeline
Tests the generate_content_with_retry function, SummaryService.summarize_document,
and the /summarize endpoint — all with mocked API calls.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Test: generate_content_with_retry (gemini_service.py)
# ---------------------------------------------------------------------------
class TestGenerateContentWithRetry(unittest.TestCase):
    """Tests for the core Gemini API wrapper function."""

    def test_missing_api_key_raises_value_error(self):
        """Calling generate_content_with_retry with no API key should raise ValueError."""
        from app.services.gemini_service import generate_content_with_retry

        with patch("app.services.gemini_service.settings") as mock_settings, \
             patch("app.services.gemini_service._client", None):
            mock_settings.GEMINI_API_KEY = ""
            with self.assertRaises(ValueError) as ctx:
                generate_content_with_retry("Prompt {text}", "Sample text")
            self.assertIn("GEMINI_API_KEY", str(ctx.exception))

    @patch("app.services.gemini_service._client")
    def test_generate_content_success(self, mock_client):
        """Happy path: API returns valid text."""
        from app.services.gemini_service import generate_content_with_retry

        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = "This is a legal document summary."
        mock_client.models.generate_content.return_value = mock_response

        with patch("app.services.gemini_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "fake-test-key"
            mock_settings.MODEL_NAME = "gemini-2.5-flash-lite"
            mock_settings.MAX_OUTPUT_TOKENS = 1024

            result = generate_content_with_retry(
                "Summarize this:\n{text}", "Test document text"
            )

        self.assertEqual(result, "This is a legal document summary.")
        mock_client.models.generate_content.assert_called_once()

    @patch("app.services.gemini_service._client")
    def test_generate_content_handles_braces_in_document_text(self, mock_client):
        """Curly braces inside legal text should not break prompt interpolation."""
        from app.services.gemini_service import generate_content_with_retry

        mock_response = MagicMock()
        mock_response.text = "Summary produced successfully."
        mock_client.models.generate_content.return_value = mock_response

        with patch("app.services.gemini_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "fake-test-key"
            mock_settings.MODEL_NAME = "gemini-2.5-flash-lite"
            mock_settings.MAX_OUTPUT_TOKENS = 1024

            legal_text = "The court observed {A} and {B} in favour of the applicant. Section 17(1) was applied."
            result = generate_content_with_retry("Summarize this:\n{text}", legal_text)

        self.assertEqual(result, "Summary produced successfully.")
        prompt_sent = mock_client.models.generate_content.call_args.kwargs["contents"]
        self.assertIn("{A}", prompt_sent)

    @patch("app.services.gemini_service._client")
    def test_generate_content_empty_response_raises(self, mock_client):
        """Empty API response should raise RuntimeError."""
        from app.services.gemini_service import generate_content_with_retry

        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response

        with patch("app.services.gemini_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "fake-test-key"
            mock_settings.MODEL_NAME = "gemini-2.5-flash-lite"
            mock_settings.MAX_OUTPUT_TOKENS = 1024

            with self.assertRaises(RuntimeError):
                generate_content_with_retry("Prompt {text}", "text")


# ---------------------------------------------------------------------------
# 2. Test: SummaryService.summarize_document (summary_service.py)
# ---------------------------------------------------------------------------
class TestSummaryService(unittest.TestCase):
    """Tests for the SummaryService orchestration layer."""

    @patch("app.services.summary_service.generate_content_with_retry")
    def test_single_shot_summarization(self, mock_generate):
        """Short text should use single-pass summarization (1 API call)."""
        from app.services.summary_service import SummaryService

        mock_generate.return_value = "Mocked Legal Summary"

        short_text = "IN THE HIGH COURT OF JUDICATURE AT MADRAS. Short text."
        result = SummaryService.summarize_document(
            filename="test.pdf", raw_text=short_text, pages=1
        )

        self.assertEqual(result["summary"], "Mocked Legal Summary")
        self.assertEqual(result["chunks_processed"], 1)
        self.assertEqual(result["gemini_requests"], 1)
        self.assertGreater(result["estimated_tokens"], 0)
        mock_generate.assert_called_once()

    @patch("app.services.summary_service.generate_content_with_retry")
    def test_map_reduce_summarization(self, mock_generate):
        """Long text exceeding MAX_INPUT_TOKENS should trigger chunked summarization."""
        from app.services.summary_service import SummaryService

        mock_generate.return_value = "Mocked Chunk Summary"

        # Create text that exceeds MAX_INPUT_TOKENS (6000 tokens ~ 24000 chars)
        large_text = ("Paragraph content for testing large text summarization.\n\n" * 600)
        result = SummaryService.summarize_document(
            filename="large.pdf", raw_text=large_text, pages=50
        )

        self.assertEqual(result["summary"], "Mocked Chunk Summary")
        self.assertGreater(result["chunks_processed"], 1)
        # chunks + 1 combine call
        self.assertGreater(result["gemini_requests"], 1)

    @patch("app.services.summary_service.generate_content_with_retry")
    def test_result_metadata_fields(self, mock_generate):
        """Result dict should contain all expected metadata keys."""
        from app.services.summary_service import SummaryService

        mock_generate.return_value = "Summary text"

        result = SummaryService.summarize_document(
            filename="doc.pdf", raw_text="Some legal content.", pages=3
        )

        expected_keys = {
            "filename", "pages", "estimated_tokens",
            "chunks_processed", "gemini_requests",
            "processing_time_seconds", "summary"
        }
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(result["filename"], "doc.pdf")
        self.assertEqual(result["pages"], 3)


# ---------------------------------------------------------------------------
# 3. Test: /summarize endpoint (routers/summarize.py)
# ---------------------------------------------------------------------------
class TestSummarizeEndpoint(unittest.TestCase):
    """Tests for the FastAPI /summarize endpoint."""

    def test_root_healthcheck_stage3(self):
        """Health check should report Stage 3."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["stage"], "Stage 3 - Gemini LLM Summarization Pipeline")

    def test_summarize_invalid_extension(self):
        """Uploading a .txt file should be rejected."""
        files = {"file": ("test.txt", b"plain text content", "text/plain")}
        response = client.post("/summarize", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file type", response.json()["detail"])

    def test_summarize_empty_file(self):
        """Uploading an empty file should be rejected."""
        files = {"file": ("test.pdf", b"", "application/pdf")}
        response = client.post("/summarize", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["detail"].lower())

    @patch("app.routers.summarize.SummaryService")
    @patch("app.routers.summarize.parse_pdf")
    def test_summarize_success_pdf(self, mock_parse_pdf, mock_summary_svc):
        """Full happy-path: upload PDF -> parse -> summarize -> 200 response."""
        mock_parse_pdf.return_value = (
            "IN THE COURT OF DISTRICT JUDGE. ORDER: Suit decreed.",
            2
        )
        mock_summary_svc.summarize_document.return_value = {
            "filename": "judgement.pdf",
            "pages": 2,
            "estimated_tokens": 150,
            "chunks_processed": 1,
            "gemini_requests": 1,
            "processing_time_seconds": 0.45,
            "summary": "Legal summary of judgment."
        }

        files = {"file": ("judgement.pdf", b"%PDF-1.4 mock content", "application/pdf")}
        response = client.post("/summarize", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["filename"], "judgement.pdf")
        self.assertEqual(data["pages"], 2)
        self.assertEqual(data["summary"], "Legal summary of judgment.")
        self.assertEqual(data["gemini_requests"], 1)

    @patch("app.routers.summarize.SummaryService")
    @patch("app.routers.summarize.parse_pdf")
    def test_summarize_api_failure_returns_500(self, mock_parse_pdf, mock_summary_svc):
        """If SummaryService raises an unexpected error, endpoint returns 500."""
        mock_parse_pdf.return_value = ("Some text", 1)
        mock_summary_svc.summarize_document.side_effect = RuntimeError("Gemini API down")

        files = {"file": ("case.pdf", b"%PDF-1.4 content", "application/pdf")}
        response = client.post("/summarize", files=files)
        self.assertEqual(response.status_code, 500)
        self.assertIn("unexpected error", response.json()["detail"].lower())


if __name__ == "__main__":
    unittest.main()
