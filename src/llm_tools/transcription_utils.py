import os
from typing import Optional, Protocol
from openai import OpenAI

from src.rate_limits.models.rate_limiter import RateLimiter


def transcribe_to_file(
    input_audio_path: str,
    output_text_path: str,
    *,
    rl: RateLimiter,
    model: str = "gpt-4o-transcribe",
    response_format: str = "text",
    prompt: Optional[str] = None,
) -> str:
    """
    Transcribes an audio file and writes the result to a text file.

    Args:
        input_audio_path: Path to your audio file (mp3, wav, m4a, etc.).
        output_text_path: Path where the transcript will be saved.
        rl: Rate limiter instance; .wait() will block until a request is allowed.
        model: One of "gpt-4o-transcribe", "gpt-4o-mini-transcribe" or "whisper-1".
        response_format: "text" or "json".
        prompt: Optional context prompt to improve transcription quality.

    Returns:
        The full transcript as a string.
    """
    # 1. Initialize the client
    client = OpenAI()

    # 2. Open audio file in binary mode
    with open(input_audio_path, "rb") as audio_file:
        # 3. Build request parameters
        params = {
            "model": model,
            "file": audio_file,
            "response_format": response_format,
        }
        if prompt:
            params["prompt"] = prompt

        # --- Block here until allowed by rate limit
        rl.wait()

        # 4. Call the Transcriptions endpoint
        transcription = client.audio.transcriptions.create(**params)

    # 5. Extract the transcript text
    transcript_text = (
        transcription.text
        if hasattr(transcription, "text")
        else transcription["text"]
    )

    # 6. Ensure output directory exists and write to output file
    os.makedirs(os.path.dirname(output_text_path) or ".", exist_ok=True)
    with open(output_text_path, "w", encoding="utf-8") as out_f:
        out_f.write(transcript_text)

    return transcript_text
