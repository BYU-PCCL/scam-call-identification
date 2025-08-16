import os
import pandas as pd

from src.ml_scam_classification.utils.cout_log_utils import (
    cout_log,
    cout_log_info
)
from src.ml_scam_classification.utils.json_utils import is_json, convert_list_json_str_to_json_list, write_json_to_file

from src.ml_scam_classification.utils.chatgpt_utils import start_conversation, continue_conversation

import sys
import os
import time
import pandas as pd
from src.ml_scam_classification.utils.file_utils import read_file
from src.ml_scam_classification.utils.json_utils import is_json, convert_list_json_str_to_json_list, write_json_to_file
from src.ml_scam_classification.utils.chatgpt_utils import (
    start_conversation,
    continue_conversation,
    build_progress_message,
    get_response_from_chatgpt,
    extract_json_from_response,
    estimate_remaining_lines
)
from src.ml_scam_classification.utils.llm_utils import get_json_from_llm_response

# -- Data Loading and Filename Generation --

def load_transcripts(csv_path):
    """Load transcripts from a CSV file."""
    return pd.read_csv(csv_path)

def generate_output_filename(base_filepath, transcript_index):
    """Generate a unique filename for output using transcript index."""
    base, ext = os.path.splitext(base_filepath)
    return f"{base}_{str(transcript_index).zfill(5)}.json"

# -- Transcript Processing --

def process_transcript_into_behaviors_json(
    transcript_text,
    transcript_index,
    main_prompt,
    cont_prompt,
    model,
    role,
    total_transcripts,
    stop_index
):
    """
    Process one transcript by:
      1. Building the full prompt (main prompt + transcript text)
      2. Starting the conversation and extracting the first JSON answer
      3. Estimating how many extra responses (lines) are needed
      4. Iteratively continuing the conversation to collect all JSON responses
    Returns a list of JSON responses.
    """
    # Add call transcript to main instructions to get first full prompt
    full_prompt = f"{main_prompt}\n\nCall Transcript:\n\n{transcript_text}"
    
    # Build progress message to print progress so far
    progress_msg = build_progress_message(stop_index, total_transcripts, transcript_index)
    print(progress_msg)
    time.sleep(1)
    print("Starting conversation... (may take up to 60 seconds)")
    conversation = start_conversation(prompt=full_prompt, system_message=role, model=model, progress_message=progress_msg)
    print("Started initial request via ChatGPT conversation.")
    
    # Get the first response from ChatGPT and extract the JSON
    response = get_response_from_chatgpt(conversation)
    json_parts = [extract_json_from_response(response)]
    
    # Estimate num additional responses required
    # The prompt instructions may or may not ask for the num of lines, if it doesn't, it will estimate
    print("Computing transcript lines remaining...")
    remaining, is_estimated = estimate_remaining_lines(response, transcript_text)
    print("N Transcript lines remaining obtained.")
    
    for line in range(remaining):
        # Build a progress message saying how many lines left
        progress_msg = build_progress_message(stop_index, total_transcripts, transcript_index, line, remaining, is_estimated)
        print(progress_msg)

        # get behaviors from each remaining line with separate prompt for each line (to avoid token limit)
        conversation = continue_conversation(conversation, cont_prompt, model, progress_message=progress_msg)
        response = get_response_from_chatgpt(conversation)

        # If no response returned, exit
        if not response.strip():
            break

        # get behavior jsons from chatgpt response
        current_json = extract_json_from_response(response)
        if not is_json(current_json):
            raise ValueError("Extracted content is not valid JSON.")
        json_parts.append(current_json)

    return json_parts

# -- Main Execution Function --

# TODO - Transcript obj parameter w/transformation fn
# TODO - add display loading


def run_chatgpt_behavioral_analysis(
    prompt_filepath,
    continuation_prompt_filepath,
    path_to_data,
    response_writepath,
    model,
    model_role,
    start_transcript_index=0,
    end_transcript_index=1, # by default only do 1 transcript
    required_transcripts_col_name="transcripts" # default... to ensure double checking what column is being used
):
    cout_log_info(1)

    # Read the prompt from file
    with open(prompt_filepath, "r") as file:
        prompt_instructions_from_file = file.read()

    cout_log_info(2)

    # Read conversation data (using only a subset for this example)
    conversations = pd.read_csv(path_to_data)

    cout_log_info(3)

    n_conversations = len(conversations)
    conversation_idx = 0

    # prepare continuation prompt so ChatGPT can know what to do when continuing to iterate over the lines
    with open(continuation_prompt_filepath, "r") as file:
        continuation_prompt_str = file.read()

    # List to store one json per transcript
    list_all_json_results = []

    # read data
    try:
        df = pd.read_csv(path_to_data)
    except Exception as e:
        print("An error occurred:", e)
    
    if (df.shape[1] > 1):
        raise Exception("Passed df with more than 1 column -- df should only contain one transcripts column at this point in processing...")
    
    if not (df.columns[0] == required_transcripts_col_name):
        raise ValueError(f"Required column name set as: {required_transcripts_col_name}, but passed df has col name: {df.columns[0]}")

    transcripts = df.iloc[:, 0]

    for curr_transcript_i, transcript_text in enumerate(transcripts):
        # Checking to see if configured to start at a later transcript... if so, need to skip if not there yet
        if conversation_idx < start_transcript_index:
            continue
        # Checking to see if configured to end before the current transcript index, if so, break out of the loop
        if conversation_idx >= end_transcript_index:
            break

        conversation_idx += 1

        cout_log_info(4)

        # Combine the system prompt with the call transcript
        complete_prompt = (
            prompt_instructions_from_file + 
            "\n\ncall transcript:\n\n" + 
            transcript_text
            )

        # Build progress cout output message
        extra = ""
        if start_transcript_index is not None and start_transcript_index > 0:
            extra = f", configured to start at call transcript {start_transcript_index + 1}"
        if end_transcript_index is not None and end_transcript_index < n_conversations:
            extra = f", configured to stop after call transcript {end_transcript_index}"
        progress_cout_output_message = (
            f"Call Transcript {conversation_idx}/{n_conversations}" + extra
        )

        # Start a new conversation for this transcript.
        # The start_conversation function will build the conversation history using the
        # system message (model_role) and the initial user prompt (complete_prompt).
        conversation = start_conversation(
            progress_message=progress_cout_output_message,
            prompt=complete_prompt,
            system_instructions=model_role,
            model=model
            # You can pass additional extra parameters here like this:
            #temperature=0.7,
            #max_tokens=200
        )

        # Retrieve the response from the conversation
        # (assumes response is in "content" field)
        response_text = conversation[-1]["content"]

        cout_log_info(5)
        cout_log_info(6)

        # ensure response contains json
        first_json = get_json_from_llm_response(response_text)

        cout_log_info(7)

        if not is_json(first_json):
            cout_log_info(8)
            raise ValueError("Critical Error: JSON not parsed correctly from ChatGPT response. Terminating.")

        # Determine how many additional iterations we need.
        # (If the response already states the total number of transcript lines, use that;
        # otherwise, estimate based on the raw transcript)
        if "Number of Lines in Cleaned Transcript in Total:" in response_text:
            # using prompt which asks ChatGPT to list n lines in cleaned transcript
            response_text_has_asterisks = response_text[-1] == '*'
            int_str = response_text.split("Number of Lines in Cleaned Transcript in Total: ")[1]
            if response_text_has_asterisks:
                # remove last 2 chars, as they are asterisks
                int_str = int_str[:-2]
            if int_str[-1] == '.':
                int_str = int_str[:-1]
            n_lines_in_cleaned_transcript = int(int_str)
            n_iterations_over_lines = n_lines_in_cleaned_transcript - 1  # subtract 1 since the first line was handled
            n_iterations_was_estimated = False
        else:
            # prompt doesn't explicitly ask ChatGPT to list num lines in cleaned transcript, assume it can't be more than 1.5 times 
            # the number of lines in the subset_of_data_append_to_prompt (the raw transcript)
            # If the response stops including additional json, the loop will stop asking ChatGPT to produce json for additional
            # transcript lines, this is just here just in case that doesn't happen to prevent an infinite loop.
            n_lines_in_raw_transcript = len(transcript_text.split('\n')) + 1
            n_iterations_over_lines = int(n_lines_in_raw_transcript * 1.5)
            n_iterations_was_estimated = True

        cout_log_info(9)

        # Store all JSON responses for this transcript in a list
        json_strings = []
        json_strings.append(first_json)

        line_idx = 0

        # Iterate over remaining lines, having ChatGPT produce the json for the behaviors
        for i in range(n_iterations_over_lines):
            # Build progress message
            progress_cout_output_message = (
                f"Conversation {conversation_idx}/{n_conversations} , "
                f"Transcript Line {i + 1}/{n_iterations_over_lines}{' - estimated' if n_iterations_was_estimated else ''}"
            )

            if end_transcript_index is not None and end_transcript_index < n_conversations:
                extra = f", configured to stop after call transcript {end_transcript_index}"
            else:
                extra = ""
            progress_cout_output_message = (
                f"Call Transcript {conversation_idx}/{n_conversations}{extra}, "
                f"Transcript Line {i + 1}/{n_iterations_over_lines}{' - estimated' if n_iterations_was_estimated else ''}"
            )

            # Use continue_conversation to add the continuation prompt.
            conversation = continue_conversation(
                progress_message=progress_cout_output_message,
                conversation=conversation,
                prompt=continuation_prompt_str,
                model=model
                # You can pass additional extra parameters here like this:
                #temperature=0.7,
                #max_tokens=200
            )

            # Get latest response
            response_text = conversation[-1]["content"]

            cout_log_info(5)

            # if response empty, return error
            if response_text == "":
                raise ValueError("Called continue_conversation(), but response was empty.")

            cout_log_info(6)

            if "```json" not in response_text:
                raise ValueError("Critical Error: Could not locate ```json in response from continuation prompt. Terminating.")
            if len(response_text) < 100 and ('done' in response_text or 'Done' in response_text):
                print("WARNING - ChatGPT indicated it was done after only one line. Please verify if this transcript has only one line.")

                cont = input("Continue (y/n)? ")

                if cont.lower() != "y":
                    print("\nTerminating... After fixing the issue, pick up where you left off by modifying the start_transcript_index parameter.")
                    return

                print("ChatGPT indicated it was done processing the transcript. Moving to the next transcript.")
                break

            # Extract JSON from the assistant response.
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

        # Combine the JSON strings from all conversation turns into a list and write to file.
        json_to_write = convert_list_json_str_to_json_list(json_strings)
        write_json_to_file(json_obj=json_to_write, output_path=response_writepath)

        cout_log_info(10)
    
    cout_log("Done.")
