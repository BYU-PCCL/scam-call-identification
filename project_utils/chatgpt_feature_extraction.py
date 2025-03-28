import sys
import os
import re
import pandas as pd
import json
import requests
from dotenv import load_dotenv

from cout_log_utils import (
    cout_log,
    cout_log_title,
    cout_log_action,
    cout_log_w_char_limit,
    cout_log_info
)
from json_utils import is_json, convert_list_json_str_to_json_list, write_json_to_file
from file_utils import get_chatgpt_api_key

from chatgpt_utils import start_conversation, continue_conversation


def run_chatgpt_behavioral_analysis(
    prompt_filepath="./data/gemini_prompt_conner_v3.txt",  # default system prompt file
    continuation_prompt_filepath="./data/gemini_prompt_conner_v3_contd.txt",
    response_writepath="./outputs/feature_extraction_chatgpt_out.txt",
    model="gpt-4o-2024-11-20",
    model_role="You are a call analysis system creating useful features to input to a scam detection model.", # default role we could use
    start_transcript_index=0,
    end_transcript_index=1
):
    cout_log_info(1)

    # Read the prompt from file
    with open(prompt_filepath, "r") as file:
        prompt_instructions_from_file = file.read()

    cout_log_info(2)

    # Read conversation data (using only a subset for this example)
    conversations = pd.read_csv('./data/call_data_by_conversation.csv')

    cout_log_info(3)

    n_conversations = len(conversations)
    conversation_idx = 0

    # prepare continuation prompt so ChatGPT can know what to do when continuing to iterate over the lines
    with open(continuation_prompt_filepath, "r") as file:
        continuation_prompt_str = file.read()

    # List to store one json per transcript
    list_all_json_results = []

    for index, row in conversations.iterrows():
        # Checking to see if configured to start at a later transcript... if so, need to skip if not there yet
        if conversation_idx < start_transcript_index:
            continue
        
        # Checking to see if configured to end before the current transcript index, if so, break out of the loop
        if conversation_idx >= end_transcript_index:
            break

        conversation_idx += 1
        transcript_text = row['TEXT'] # assuming in column 'TEXT'

        cout_log_info(4)

        # Combine the system prompt with the call transcript
        complete_prompt = (
            prompt_instructions_from_file + 
            "\n\ncall transcript:\n\n" + 
            transcript_text
            )

        # Build progress cout output message
        if end_transcript_index is not None and end_transcript_index < n_conversations:
            extra = f", configured to stop after call transcript {end_transcript_index}"
        else:
            extra = ""
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

        # Validate that the response contains the expected JSON formatting.
        # (In our design, we assume the assistant returns JSON wrapped between ```json\n and \n```.)
        if "```json" not in response_text:
            raise ValueError("Critical Error: Could not locate ```json in the response, meaning the response likely contains no valid json. Terminating.")
        # Extract the JSON portion.
        try:
            json_and_rest = response_text.split("```json\n")[1]
            json_only = json_and_rest.split("\n```")[0]
        except IndexError:
            if len(response) < 100 and ('done' in response or 'Done' in response):
                print("WARNING - ChatGPT indicated it was done after only one line. This is fine so long as the current transcript is only one line, but please double check.")

                cont = input("Continue (y/n)?")

                if cont != "Y" and cont != "Y":
                    return
                
                print("ChatGPT indicated it was done processing the transcript. Moving to the next transcript.")
                continue
            raise ValueError("Critical Error: JSON delimiters not found as expected in the response.")

        first_json = json_only

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

       # Prepare a unique file name for the output for this transcript.
        filename_without_ext, _ = os.path.splitext(response_writepath)
        filename_suffix_number = str(conversation_idx).zfill(5)
        dest_path = f"{filename_without_ext}_{filename_suffix_number}.json"

        # Combine the JSON strings from all conversation turns into a list and write to file.
        json_to_write = convert_list_json_str_to_json_list(json_strings)
        write_json_to_file(json_obj=json_to_write, output_path=dest_path)

        cout_log_info(10)
    
    cout_log("Done.")


if __name__ == "__main__":
    n_args = len(sys.argv)
    if n_args == 1:
        run_chatgpt_behavioral_analysis()
    elif n_args == 2:
        run_chatgpt_behavioral_analysis(sys.argv[1])
    elif n_args == 3:
        run_chatgpt_behavioral_analysis(sys.argv[1], sys.argv[2])
