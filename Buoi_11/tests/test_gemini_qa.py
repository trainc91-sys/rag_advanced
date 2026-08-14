import unittest
from unittest.mock import patch

from google.api_core import exceptions as google_exceptions

import gemini_qa


class GeminiQaTests(unittest.TestCase):
    def test_answer_question_returns_fallback_on_quota_error(self):
        class FakeModel:
            def __init__(self, *args, **kwargs):
                pass

            def generate_content(self, prompt):
                raise google_exceptions.ResourceExhausted("quota exceeded")

        with patch.object(gemini_qa, "_ensure_configured", return_value=None), patch.object(
            gemini_qa.genai, "GenerativeModel", side_effect=FakeModel
        ):
            result = gemini_qa.answer_question("question", "context", model_name="test-model")

        self.assertIn("Không thể gọi Gemini", result)
        self.assertIn("quota exceeded", result.lower())


if __name__ == "__main__":
    unittest.main()
