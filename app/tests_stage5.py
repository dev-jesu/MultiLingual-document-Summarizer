import unittest
from unittest.mock import patch

from app.prompts.summary_prompt import build_summary_prompt
from app.prompts.translation_prompt import build_translation_prompt
from app.services.language_detection import detect_language, normalize_language_parameters, UnsupportedLanguageError
from app.services.translation_service import TranslationService


class TestStage5MultilingualSupport(unittest.TestCase):
    def test_detects_supported_indian_languages(self):
        self.assertEqual(detect_language("यह न्यायालय यह मामला देख रहा है।"), "hi")
        self.assertEqual(detect_language("న్యాయస్థానం ఈ కేసును పరిశీలించింది."), "te")
        self.assertEqual(detect_language("ನ್ಯಾಯಾಲಯ ಈ ಪ್ರಕರಣವನ್ನು ಪರಿಗಣించింది."), "kn")
        self.assertEqual(detect_language("ന്യായാലയം ഈ കേസിനെ പരിഗണിച്ചു."), "ml")
        self.assertEqual(detect_language("न्यायालयाने या प्रकरणात निर्णय दिला."), "mr")

    def test_supports_manual_override_over_detection(self):
        self.assertEqual(detect_language("This is an English case summary.", preferred_language="hi"), "hi")

    def test_invalid_language_is_rejected(self):
        with self.assertRaises(UnsupportedLanguageError):
            normalize_language_parameters("fr", "en")

    def test_builds_dynamic_summary_prompt_for_target_language(self):
        prompt = build_summary_prompt("hi", "sample text")
        self.assertIn("हिंदी", prompt)
        self.assertIn("sample text", prompt)

    def test_builds_dynamic_translation_prompt_for_language_pair(self):
        prompt = build_translation_prompt("en", "ml", "sample text")
        self.assertIn("മലയാളം", prompt)
        self.assertIn("sample text", prompt)

    @patch("app.services.translation_service.generate_content_with_retry")
    def test_translation_service_uses_prompt_for_supported_pair(self, mock_generate):
        mock_generate.return_value = "Translated summary"

        result = TranslationService.translate_summary(
            text="A legal summary.",
            source_language="en",
            target_language="hi",
        )

        self.assertEqual(result, "Translated summary")
        self.assertEqual(mock_generate.call_count, 1)


if __name__ == "__main__":
    unittest.main()
