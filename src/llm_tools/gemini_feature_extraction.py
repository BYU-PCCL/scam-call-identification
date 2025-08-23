import os
import time
import pandas as pd
from typing import Protocol

from google import genai
from google.genai import types

from src.rate_limits.models.rate_limiter import RateLimiter
from src.ml_scam_classification.utils.file_utils import (
    get_gemini_api_key,
    ensure_file_versioning_ok,
)
from src.llm_tools.llm_utils import get_json_from_llm_response


NS_PER_MINUTE = 60_000_000_000  # 60 seconds in ns

def run_gemini_behavioral_analysis(
    *,
    prompt_filepath: str,
    response_writepath: str,
    rl: RateLimiter,
) -> None:
    """
    Run Gemini behavioral analysis with strict rate limiting.

    Parameters
    ----------
    prompt_filepath : str
        Path to the system prompt file (text).
    response_writepath : str
        Path to append JSON responses.
    rl : RateLimiterLike
        An object providing a .wait() method that blocks until a request is allowed.
    """
    if not isinstance(prompt_filepath, str) or not isinstance(response_writepath, str):
        raise ValueError("ERROR - Expected string paths for prompt_filepath and response_writepath.")
    if not os.path.exists(prompt_filepath):
        raise FileNotFoundError(f"Prompt file does not exist: {prompt_filepath}")
    if not hasattr(rl, "wait"):
        raise TypeError("Rate limit object must provide a .wait() method.")

    # Optional: ensure write path/versioning is okay for appends
    ensure_file_versioning_ok(response_writepath)

    # Set up Google Gemini (API key from .env)
    key = get_gemini_api_key()
    client = genai.Client(api_key=key)

    with open(prompt_filepath, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    conversations = pd.read_csv(
        "src/ml_scam_classification/data/call_data_by_conversation/processed/call_data_by_conversation.csv"
    )
    conversations_small = conversations[:2]

    for _, row in conversations_small.iterrows():
        complete_prompt = f"{system_prompt}\n\ncall transcript:\n\n{row['TEXT']}"
        print("complete prompt:")
        print(complete_prompt)

        # --- BLOCK HERE until allowed by rate limit
        rl.wait()

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=complete_prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=32768)
            ),
        )
        print(response)

        json_str = get_json_from_llm_response(response.text)

        # Append JSON result per conversation
        with open(response_writepath, "a", encoding="utf-8") as f:
            f.write(json_str)
            f.write("\n")  # separator per record
