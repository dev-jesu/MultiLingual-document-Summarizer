import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestStage7Export(unittest.TestCase):
    def setUp(self):
        self.sample_payload = {
            "filename": "judgement.pdf",
            "summary": "IN THE HIGH COURT OF JUDICATURE AT MADRAS\n\n1. Facts of the case...\n2. Legal judgment...",
            "language": "ta",
            "processing_time": "18.4s"
        }

    def test_export_pdf_success(self):
        response = client.post("/export/pdf", json=self.sample_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertIn('attachment; filename="judgement_summary.pdf"', response.headers["content-disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_export_docx_success(self):
        response = client.post("/export/docx", json=self.sample_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertIn('attachment; filename="judgement_summary.docx"', response.headers["content-disposition"])
        self.assertTrue(response.content.startswith(b"PK"))  # DOCX is zip file format

    def test_export_txt_success(self):
        response = client.post("/export/txt", json=self.sample_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.headers["content-type"])
        self.assertIn('attachment; filename="judgement_summary.txt"', response.headers["content-disposition"])
        text_output = response.content.decode("utf-8")
        self.assertIn("District Court e-Services", text_output)
        self.assertIn("judgement.pdf", text_output)
        self.assertIn("IN THE HIGH COURT OF JUDICATURE AT MADRAS", text_output)

    def test_export_multilingual_indian_languages(self):
        languages_samples = [
            ("ta", "வணக்கம் - நீதிமன்றத் தீர்ப்பு சுருக்கம்."),
            ("hi", "नमस्ते - उच्च न्यायालय का निर्णय।"),
            ("te", "నమస్కారం - తీర్పు సారాంశం."),
            ("kn", "ನಮಸ್ಕಾರ - ನ್ಯಾಯಾಲಯದ ತೀರ್ಪು."),
            ("ml", "നമസ്കാരം - കോടതി വിധി സംഗ്രഹം."),
            ("mr", "नमस्कार - न्यायालयाचा निर्णय."),
            ("en", "Legal Judgment Summary for District Court.")
        ]

        for lang, text in languages_samples:
            payload = {
                "filename": f"sample_{lang}.pdf",
                "summary": text,
                "language": lang,
                "processing_time": "5.2s"
            }

            # Test PDF
            res_pdf = client.post("/export/pdf", json=payload)
            self.assertEqual(res_pdf.status_code, 200, f"PDF export failed for {lang}")
            self.assertTrue(res_pdf.content.startswith(b"%PDF"))

            # Test DOCX
            res_docx = client.post("/export/docx", json=payload)
            self.assertEqual(res_docx.status_code, 200, f"DOCX export failed for {lang}")
            self.assertTrue(res_docx.content.startswith(b"PK"))

            # Test TXT
            res_txt = client.post("/export/txt", json=payload)
            self.assertEqual(res_txt.status_code, 200, f"TXT export failed for {lang}")
            self.assertIn(text, res_txt.content.decode("utf-8"))

    def test_export_empty_summary_returns_400(self):
        bad_payload = {
            "filename": "test.pdf",
            "summary": "   ",
            "language": "en",
            "processing_time": "1.0s"
        }
        res_pdf = client.post("/export/pdf", json=bad_payload)
        self.assertEqual(res_pdf.status_code, 400)

        res_docx = client.post("/export/docx", json=bad_payload)
        self.assertEqual(res_docx.status_code, 400)

        res_txt = client.post("/export/txt", json=bad_payload)
        self.assertEqual(res_txt.status_code, 400)


if __name__ == "__main__":
    unittest.main()
