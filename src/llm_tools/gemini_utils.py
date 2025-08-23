import os
from typing import Protocol

from dotenv import load_dotenv
from google import genai

from src.ml_scam_classification.utils.file_utils import get_gemini_api_key
from src.rate_limits.models.rate_limiter import RateLimiter


def run_simple_gemini_test(
    *,
    rl: RateLimiter,
    output_file: str = "./outputs/gemini_test_output.txt",
) -> None:
    """
    Minimal Gemini call that respects an injected rate limiter.

    Parameters
    ----------
    rl : RateLimiterLike
        Rate limiter instance; .wait() will block until a request is allowed.
    output_file : str
        File path to write the response text.
    """
    # Load environment and fetch API key
    load_dotenv()
    key = get_gemini_api_key()

    # Initialize client with API key
    client = genai.Client(api_key=key)

    # Block here until we're allowed to make a request
    rl.wait()

    # Make the request
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="what fruits are most similar to pineapples",
    )

    # Ensure output directory exists and write response
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.text)


if __name__ == "__main__":
    # Example usage: import your project-specific rate limiter singleton and run
    #
    # from settings.ratelimits import GEMINI_2_5_PRO_5RPM
    # run_simple_gemini_test(rl=GEMINI_2_5_PRO_5RPM)
    #
    # Keeping __main__ empty avoids hard-coding a specific settings dependency here.
    pass
