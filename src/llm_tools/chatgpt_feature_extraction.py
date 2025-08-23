import os
import time
from typing import Protocol, Optional

import pandas as pd

from src.rate_limits.models.rate_limiter import RateLimiter
from src.llm_tools.debug_utils import cout_log, cout_log_info
from src.ml_scam_classification.utils.json_utils import (
    is_json,
    convert_list_json_str_to_json_list,
    write_json_to_file,
)
from src.llm_tools.chatgpt_utils import (
    start_conversation,
    continue_conversation,
    build_progress_message,
    get_response_from_chatgpt_conversation,
    estimate_remaining_lines,
)
from src.llm_tools.llm_utils import get_json_from_llm_response

# -- Data Loading and Filename Generation --

def load_transcripts(csv_path: str) -> pd.DataFrame:
    """Load transcripts from a CSV file."""
    return pd.read_csv(csv_path)

def generate_output_filename(base_filepath: str, transcript_index: int) -> str:
    """Generate a unique filename for output using transcript index."""
    base, ext = os.path.splitext(base_filepath)
    return f"{base}_{str(transcript_index).zfill(5)}.json"


# -- Transcript Processing --

def process_transcript_into_behaviors_json(
    transcript_text: str,
    transcript_index: int,
    main_prompt: str,
    cont_prompt: str,
    model: str,
    role: Optional[str],
    total_transcripts: int,
    stop_index: Optional[int],
    *,
    rl: RateLimiter,
):
    """
    Process one transcript by:
      1) Building the full prompt (main prompt + transcript text)
      2) Starting the conversation and extracting the first JSON answer
      3) Estimating how many extra responses (lines) are needed
      4) Iteratively continuing the conversation to collect all JSON responses
    Returns a list of JSON responses (as strings).
    """
    # Add call transcript to main instructions to get first full prompt
    full_prompt = f"{main_prompt}\n\nCall Transcript:\n\n{transcript_text}"

    # Build progress message to print progress so far
    progress_msg = build_progress_message(stop_index, total_transcripts, transcript_index)
    print(progress_msg)
    time.sleep(1)
    print("Starting conversation... (may take up to 60 seconds)")

    # Start conversation (rate-limited inside start_conversation via rl)
    conversation = start_conversation(
        progress_message=progress_msg,
        prompt=full_prompt,
        rl=rl,                      # <-- inject rate limiter
        system_instructions=role,
        model=model,
    )
    print("Started initial request via ChatGPT conversation.")

    # Get the first response and extract JSON
    response = get_response_from_chatgpt_conversation(conversation)
    first_json = get_json_from_llm_response(response)
    if not is_json(first_json):
        raise ValueError("Extracted content is not valid JSON from initial response.")
    json_parts = [first_json]

    # Estimate how many additional responses are required
    print("Computing transcript lines remaining...")
    remaining, is_estimated = estimate_remaining_lines(response, transcript_text)
    print("N Transcript lines remaining obtained.")

    for line in range(remaining):
        # Build progress message (extended info)
        progress_msg = (
            f"{build_progress_message(stop_index, total_transcripts, transcript_index)}, "
            f"Transcript Line {line + 1}/{remaining}{' - estimated' if is_estimated else ''}"
        )
        print(progress_msg)

        # Continue conversation for each remaining line (rate-limited inside continue_conversation via rl)
        conversation = continue_conversation(
            progress_message=progress_msg,
            conversation=conversation,
            prompt=cont_prompt,
            rl=rl,                   # <-- inject rate limiter
            model=model,
        )
        response = get_response_from_chatgpt_conversation(conversation)

        # If no response returned, exit loop
        if not response.strip():
            break

        # Extract JSON
        current_json = get_json_from_llm_response(response)
        if not is_json(current_json):
            raise ValueError("Extracted content is not valid JSON from continuation response.")
        json_parts.append(current_json)

    return json_parts


# -- Main Execution Function --

def run_chatgpt_behavioral_analysis(
    prompt_filepath: str,
    continuation_prompt_filepath: str,
    path_to_data: str,
    response_writepath: str,
    model: str,
    model_role: Optional[str],
    *,
    rl: RateLimiter,
    start_transcript_index: int = 0,
    end_transcript_index: int = 1,       # by default only do 1 transcript
    required_transcripts_col_name: str = "transcripts",  # double-check column used
):
    cout_log_info(1)

    # Read prompts
    with open(prompt_filepath, "r", encoding="utf-8") as file:
        prompt_instructions_from_file = file.read()

    with open(continuation_prompt_filepath, "r", encoding="utf-8") as file:
        continuation_prompt_str = file.read()

    cout_log_info(2)

    # Load data
    try:
        df = pd.read_csv(path_to_data)
    except Exception as e:
        raise RuntimeError(f"Failed to read CSV at {path_to_data}") from e

    cout_log_info(3)

    if df.shape[1] > 1:
        raise ValueError(
            "Passed df with more than 1 column -- df should only contain one transcripts column at this point in processing..."
        )
    if df.columns[0] != required_transcripts_col_name:
        raise ValueError(
            f"Required column name set as: {required_transcripts_col_name}, but passed df has col name: {df.columns[0]}"
        )

    transcripts = df.iloc[:, 0]
    n_conversations = len(transcripts)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(response_writepath) or ".", exist_ok=True)

    conversation_idx = 0
    list_all_json_results = []

    for transcript_text in transcripts:
        # Skip until start index
        if conversation_idx < start_transcript_index:
            conversation_idx += 1
            continue
        # Stop when reaching end index
        if conversation_idx >= end_transcript_index:
            break

        conversation_idx += 1

        cout_log_info(4)

        # Build progress message
        extra = ""
        if start_transcript_index is not None and start_transcript_index > 0:
            extra = f", configured to start at call transcript {start_transcript_index + 1}"
        if end_transcript_index is not None and end_transcript_index < n_conversations:
            extra = f", configured to stop after call transcript {end_transcript_index}"
        progress_cout_output_message = f"Call Transcript {conversation_idx}/{n_conversations}" + extra

        # Start a new conversation for this transcript (rate-limited inside)
        conversation = start_conversation(
            progress_message=progress_cout_output_message,
            prompt=f"{prompt_instructions_from_file}\n\ncall transcript:\n\n{transcript_text}",
            rl=rl,                        # <-- inject rate limiter
            system_instructions=model_role,
            model=model,
        )

        # Retrieve the response and ensure JSON
        response_text = conversation[-1]["content"]

        cout_log_info(5)
        cout_log_info(6)

        first_json = get_json_from_llm_response(response_text)

        cout_log_info(7)

        if not is_json(first_json):
            cout_log_info(8)
            raise ValueError("Critical Error: JSON not parsed correctly from ChatGPT response. Terminating.")

        # Determine number of iterations
        if "Number of Lines in Cleaned Transcript in Total:" in response_text:
            response_text_has_asterisks = response_text[-1] == "*"
            int_str = response_text.split("Number of Lines in Cleaned Transcript in Total: ")[1]
            if response_text_has_asterisks:
                int_str = int_str[:-2]    # remove last 2 chars (asterisks)
            if int_str[-1] == ".":
                int_str = int_str[:-1]
            n_lines_in_cleaned_transcript = int(int_str)
            n_iterations_over_lines = n_lines_in_cleaned_transcript - 1  # subtract 1 since the first line was handled
            n_iterations_was_estimated = False
        else:
            n_lines_in_raw_transcript = len(transcript_text.split("\n")) + 1
            n_iterations_over_lines = int(n_lines_in_raw_transcript * 1.5)
            n_iterations_was_estimated = True

        cout_log_info(9)

        # Collect JSON results
        json_strings = [first_json]

        for i in range(n_iterations_over_lines):
            # Progress message per line
            if end_transcript_index is not None and end_transcript_index < n_conversations:
                extra = f", configured to stop after call transcript {end_transcript_index}"
            else:
                extra = ""
            progress_cout_output_message = (
                f"Call Transcript {conversation_idx}/{n_conversations}{extra}, "
                f"Transcript Line {i + 1}/{n_iterations_over_lines}"
                f"{' - estimated' if n_iterations_was_estimated else ''}"
            )

            # Continue conversation (rate-limited inside)
            conversation = continue_conversation(
                progress_message=progress_cout_output_message,
                conversation=conversation,
                prompt=continuation_prompt_str,
                rl=rl,                     # <-- inject rate limiter
                model=model,
            )

            # Latest response
            response_text = conversation[-1]["content"]

            cout_log_info(5)

            if response_text == "":
                raise ValueError("Called continue_conversation(), but response was empty.")

            cout_log_info(6)

            if "```json" not in response_text:
                raise ValueError("Critical Error: Could not locate ```json in response from continuation prompt. Terminating.")
            if len(response_text) < 100 and ("done" in response_text or "Done" in response_text):
                print("WARNING - ChatGPT indicated it was done after only one line. Please verify if this transcript has only one line.")
                cont = input("Continue (y/n)? ")
                if cont.lower() != "y":
                    print("\nTerminating... After fixing the issue, pick up where you left off by modifying the start_transcript_index parameter.")
                    return
                print("ChatGPT indicated it was done processing the transcript. Moving to the next transcript.")
                break

            # Extract JSON from assistant response
            try:
                json_and_rest = response_text.split("```json\n")[1]
                current_line_json = json_and_rest.split("\n```")[0]
            except IndexError:
                raise ValueError("Critical Error: JSON delimiters not found in continuation response. Terminating.")

            cout_log_info(7)

            if not is_json(current_line_json):
                cout_log_info(8)
                raise ValueError("Critical Error: JSON not parsed correctly from continuation response. Exiting.")

            json_strings.append(current_line_json)

        # Write combined JSON list to file
        json_to_write = convert_list_json_str_to_json_list(json_strings)
        write_json_to_file(json_obj=json_to_write, output_path=response_writepath)

        cout_log_info(10)

    cout_log("Done.")
