import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMultilingualSupport(unittest.TestCase):
    def test_detect_language_english(self):
        from app.services.language_detection import detect_language

        detected = detect_language("The court observed that the petitioner was entitled to relief.")
        self.assertEqual(detected, "en")

    def test_detect_language_tamil(self):
        from app.services.language_detection import detect_language

        detected = detect_language("நீதிமன்றம் மனுதாரர் உரிமை பெற்றார் என்று குறிப்பிட்டது.")
        self.assertEqual(detected, "ta")

    def test_detect_language_mixed_language_raises(self):
        from app.services.language_detection import detect_language

        with self.assertRaises(ValueError):
            detect_language("The court observed that the petitioner was entitled to relief. நீதிமன்றம்")

    @patch("app.services.translation_service.generate_content_with_retry")
    def test_translate_summary_uses_correct_prompt(self, mock_generate):
        from app.services.translation_service import TranslationService

        mock_generate.return_value = "சுருக்கம்"

        result = TranslationService.translate_summary(
            text="A summary of the case.",
            source_language="en",
            target_language="ta"
        )

        self.assertEqual(result, "சுருக்கம்")
        self.assertEqual(mock_generate.call_count, 1)

    @patch("app.routers.summarize.SummaryService")
    @patch("app.routers.summarize.parse_pdf")
    def test_summarize_endpoint_accepts_language_params(self, mock_parse_pdf, mock_summary_svc):
        mock_parse_pdf.return_value = (
            "IN THE COURT OF DISTRICT JUDGE. ORDER: Suit decreed.",
            1,
            None,
        )
        mock_summary_svc.summarize_document.return_value = {
            "filename": "judgement.pdf",
            "pages": 1,
            "estimated_tokens": 150,
            "chunks_processed": 1,
            "gemini_requests": 1,
            "processing_time_seconds": 0.45,
            "summary": "Legal summary of judgment."
        }

        files = {"file": ("judgement.pdf", b"%PDF-1.4 mock content", "application/pdf")}
        response = client.post(
            "/summarize",
            files=files,
            data={"source_language": "auto", "target_language": "ta"},
        )

        self.assertEqual(response.status_code, 200)
        mock_summary_svc.summarize_document.assert_called_once()
        kwargs = mock_summary_svc.summarize_document.call_args.kwargs
        self.assertEqual(kwargs["source_language"], "auto")
        self.assertEqual(kwargs["target_language"], "ta")


if __name__ == "__main__":
    unittest.main()
