from openai import OpenAI
from typing import Optional

def transcribe_to_file(
    input_audio_path: str,
    output_text_path: str,
    model: str = "gpt-4o-transcribe",
    response_format: str = "text",
    prompt: Optional[str] = None
) -> str:
    """
    Transcribes an audio file and writes the result to a text file.

    Args:
        input_audio_path: Path to your audio file (mp3, wav, m4a, etc.).
        output_text_path: Path where the transcript will be saved.
        model: One of "gpt-4o-transcribe", "gpt-4o-mini-transcribe" or "whisper-1".
        response_format: "text" or "json" (note: GPT-4o snapshots only support text/json).
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

        # 4. Call the Transcriptions endpoint
        transcription = client.audio.transcriptions.create(**params)

    # 5. Extract the transcript text
    #    Depending on response_format and SDK version this may be an attribute or a dict key
    transcript_text = (
        transcription.text
        if hasattr(transcription, "text")
        else transcription["text"]
    )

    # 6. Write to output file
    with open(output_text_path, "w", encoding="utf-8") as out_f:
        out_f.write(transcript_text)

    return transcript_text