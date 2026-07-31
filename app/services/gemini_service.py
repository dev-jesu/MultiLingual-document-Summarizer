from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings
from app.utils.logger import logger

# Initialize the Gemini API client globally
_client = None
if settings.GEMINI_API_KEY:
    _client = genai.Client(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set. API calls will fail.")


@retry(
    stop=stop_after_attempt(settings.MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def generate_content_with_retry(prompt: str, text: str) -> str:
    """
    Calls the Gemini API to generate content based on a prompt and input text.
    Implements exponential backoff and retry logic using tenacity.

    Args:
        prompt (str): The instruction prompt template (must contain {text} placeholder).
        text (str): The input text to be inserted into the prompt.

    Returns:
        str: The generated content (summary).

    Raises:
        ValueError: If the API key is missing or invalid.
        RuntimeError: If the API call fails after maximum retries.
    """
    if not settings.GEMINI_API_KEY or _client is None:
        raise ValueError("GEMINI_API_KEY is missing. Please configure it in the environment.")

    try:
        full_prompt = prompt.format(text=text)

        generation_config = types.GenerateContentConfig(
            max_output_tokens=settings.MAX_OUTPUT_TOKENS,
            temperature=0.3,  # Low temperature for factual, objective summaries
        )

        response = _client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=full_prompt,
            config=generation_config,
        )

        if not response.text:
            raise RuntimeError("Received empty response from Gemini API.")

        return response.text.strip()

    except ValueError:
        raise
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        raise
