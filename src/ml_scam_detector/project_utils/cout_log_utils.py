from dotenv import load_dotenv
from src.ml_scam_detector.project_utils.file_utils import cout_logging_enabled
import inspect

def cout_log(cout_log_str, force=False):
    if cout_logging_enabled() or force:
        print(cout_log_str)

def cout_log_action(cout_log_str, force=False, no_end_newline=False):
    if cout_logging_enabled() or force:
        print(f"\n      -> {cout_log_str}{"" if no_end_newline else "\n"}")

def cout_log_title(title_str, force=False):
    WIDTH = 75
    SEPARATION_CHAR = '-'
    if cout_logging_enabled() or force:
        if title_str[-1] == "\n":
            # embedding in format structure, get rid of extra newline at end for formatting purposes
            title_str = title_str[:-1]

        # ensure not too long to format as title
        if len(title_str) > WIDTH - 2:
            raise ValueError(f"Attempted to cout_log title_str with more than {WIDTH - 2} chars, will not fit in formatted structure")

        # print embedded in formatting structure
        print(SEPARATION_CHAR*WIDTH)
        n_padding_chars_l = (WIDTH - len(title_str)) // 2
        n_padding_chars_r = (WIDTH - len(title_str)) - n_padding_chars_l
        print(f"{" "*n_padding_chars_l + title_str + " "*n_padding_chars_r}")
        print(f"{SEPARATION_CHAR*WIDTH}\n")


def cout_log_w_char_limit(cout_log_str, char_limit, force=False):
    if cout_logging_enabled() or force:
        print(f"{cout_log_str[:char_limit]}{f"\n{"            " if "\n" in cout_log_str else ""}... (output truncated)" if len(cout_log_str) > char_limit else ""}\n")



if __name__ == "__main__":
    print("Testing cout_log function:")
    if cout_logging_enabled():
        print("found that cout_logging was enabled.")
        print("Printing test cout_log...")
        cout_log(" - If this prints, cout_logs are working. - ")
        print("If cout_logs are working, it should have just printed a message.")
    if not cout_logging_enabled():
        print("found cout_logging is not enabled.")


def get_caller_name():
    frame = inspect.currentframe()
    try:
        # Go back two frames to skip the print function call
        caller_frame = frame.f_back.f_back
        if caller_frame is not None:
            return caller_frame.f_code.co_name
        else:
            return None
    finally:
        del frame  # Break the reference cycle immediately


def cout_log_info(cout_log_num):
    func_called_from_id = get_caller_name()

    caller_frame = inspect.currentframe().f_back
    try:
        caller_vars = caller_frame.f_locals
        current_locals = {}
        
        for var_name, var_value in caller_vars.items():
            current_locals[var_name] = var_value

        # Log info

        if func_called_from_id == "run_chatgpt_behavioral_analysis":
            if cout_log_num == 1:
                cout_log_title("RUNNING CHATGPT BEHAVIORAL ANALYSIS\n")
                cout_log("Params:")
                cout_log(f"   prompt_filepath: \"{current_locals["prompt_filepath"]}\"")
                cout_log(f"   response_writepath: \"{current_locals["response_writepath"]}\"")
                cout_log(f"   model: \"{current_locals["model"]}\"")
                cout_log(f"   model_role: \"{current_locals["model_role"]}\"\n")
            elif cout_log_num == 2:
                cout_log_title(f"RECEIVED SYSTEM PROMPT:\n")
                cout_log_w_char_limit(current_locals["prompt_instructions_from_file"], 500)
            elif cout_log_num == 3:
                cout_log_title(f"DATA EXTRACTED FROM FILE:\n")
                cout_log_w_char_limit(current_locals["conversations"], 1000)
            elif cout_log_num == 4:
                cout_log_title("SUBSET OF DATA BEING APPENDED TO PROMPT:\n")
                #cout_log_w_char_limit(current_locals["subset_of_data_append_to_prompt"], 1000) # TODO update to the new attr name in case of uncomment (was updated in chatgpt_feature_extraction.py)
                # For now, I don't want to limit this log length
                cout_log(current_locals["transcript_text"])
                cout_log_action("Constructing complete prompt...")
            elif cout_log_num == 5:
                cout_log_title("FULL RESPONSE TEXT:")
                cout_log(current_locals["response_text"])
                print("\n")
            elif cout_log_num == 6:
                cout_log_title(f"RESPONSE:\n")
                cout_log_w_char_limit(current_locals["response_text"], 1000)
                cout_log(f"Writing response to output file \"{current_locals["response_writepath"]}\"")
            elif cout_log_num == 7:
                cout_log_title("JSON FROM CURRENT LINE OF TRANSCRIPT")
                cout_log(current_locals["first_json"])
            elif cout_log_num == 8:
                cout_log_title("WARNING: Unexpected Response Format - json not parsed correctly from ChatGPT response...", force=True)
                cout_log_title("Snippet gotten while attempting to extract json:", force=True)
                cout_log(current_locals["first_json"])
                cout_log("Full Response:", force=True)
                cout_log(current_locals["response_text"])
            elif cout_log_num == 9:
                cout_log(f"Performing Iterations. Number of iterations (ChatGPT-indicated or estimated number of lines in cleaned transcript): {current_locals["n_iterations_over_lines"]}")
            elif cout_log_num == 10:
                cout_log(f"Finished writing response to output file: \"{current_locals["response_writepath"]}\" for conversation {current_locals["conversation_idx"]}\n")
        elif func_called_from_id == "send_prompt_to_chatgpt":
            if cout_log_num == 1:
                cout_log_action("Fetching API Key from .env file...")
            elif cout_log_num == 2:
                cout_log("Received ChatGPT API Key:")
                cout_log_w_char_limit(current_locals["openai_api_key"], 9)
                cout_log_action("Sending prompt to ChatGPT... (may take up to 60s).", force=False, no_end_newline=True)
                cout_log(f"(Progress: {current_locals['progress_message']})")
        elif func_called_from_id == "start_conversation":
            if cout_log_num == 1:
                cout_log_action("Fetching API Key from .env file...")
            if cout_log_num == 2:
                cout_log("Received ChatGPT API Key:")
                cout_log_w_char_limit(current_locals["API_KEY"], 9)
                cout_log_action("Sending prompt to ChatGPT... (may take up to 60s).", force=False, no_end_newline=True)
                cout_log(f"(Progress: {current_locals['progress_message']})")
        elif func_called_from_id == "continue_conversation":
            if cout_log_num == 1:
                cout_log_action("Fetching API Key from .env file...")
            if cout_log_num == 2:
                cout_log("Received ChatGPT API Key:")
                cout_log_w_char_limit(current_locals["API_KEY"], 9)
                cout_log_action("Sending prompt to ChatGPT... (may take up to 60s).", force=False, no_end_newline=True)
                cout_log(f"(Progress: {current_locals['progress_message']})")
        

    finally:
        del caller_frame
    
