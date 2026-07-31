import unittest
from app.services.cleaner import clean_legal_text
from app.services.chunking import split_by_paragraphs, merge_small_chunks, chunk_document

class TestStage2Pipeline(unittest.TestCase):

    def test_clean_legal_text(self):
        raw = "IN THE COURT OF DISTRICT JUDGE\nPAGE 1 OF 5\n\nStrictly Confidential\n\nParagraph 1 text."
        cleaned = clean_legal_text(raw)
        self.assertNotIn("PAGE 1 OF 5", cleaned)
        self.assertNotIn("Strictly Confidential", cleaned)
        self.assertIn("IN THE COURT OF DISTRICT JUDGE", cleaned)
        self.assertIn("Paragraph 1 text.", cleaned)

    def test_chunking_strategy(self):
        sample_text = "Paragraph 1 line.\n\nParagraph 2 line.\n\nParagraph 3 line."
        chunks = split_by_paragraphs(sample_text)
        self.assertEqual(len(chunks), 3)

        merged = merge_small_chunks(chunks, max_tokens=100)
        self.assertTrue(len(merged) >= 1)

    def test_chunk_document_unified(self):
        pages = ["Page 1 text here.", "Page 2 text here."]
        full = "\n\n".join(pages)
        # Use a small max_tokens to force pages into separate chunks
        chunks = chunk_document(full, pages_text=pages, strategy="page", max_tokens=5)
        self.assertEqual(len(chunks), 2)

if __name__ == "__main__":
    unittest.main()
