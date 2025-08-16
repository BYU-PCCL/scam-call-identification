import sys
import time

from src.ml_scam_classification.utils.chatgpt_feature_extraction import run_chatgpt_behavioral_analysis
from src.ml_scam_classification.utils.file_utils import ensure_file_versioning_ok

if __name__ == "__main__":
    # TEMP WARNING UNTIL GET API KEY

    # TODO - rate limiting and caching

    n_args = len(sys.argv)
    if n_args > 3:
        raise ValueError("Too many arguments. usage: script.py <path_to_prompt>(opt.) <path_to_continuation_prompt>(opt.)")

    # SETTINGS
    PROMPT_FOLDER_LOCATION = "src/ml_scam_classification/prompting"
    VERSION_TO_USE = 3
    SELECTED_PROMPT_PATH = "src/ml_scam_classification/prompting/prompt_conner_v7.txt" if n_args < 2 else sys.argv[1]
    SELECTED_PROMPT_CONT_PATH = "src/ml_scam_classification/prompting/prompt_conner_v7_contd.txt" if n_args < 3 else sys.argv[2]
    PATH_TO_CONV_DATA = "src/ml_scam_classification/data/call_data_by_conversation/raw_data/call_data_by_conversation_conv_only.csv"

    ######## MASTER SETTINGS - careful when adjusting these as they may have filesystem implications
    PROMPT_FILE_ID_SUBSTR = "prompt" # Assuming all prompt files contain kw: "prompt" somewhere in filename
    VERSIONING_PREFIX = "_v"
    FORCE_ACCEPT_NONMAX_VERSION = False # Will prompt user to double-check if set to true
    RESPONSE_WRITEPATH = f"src/ml_scam_classification/outputs/{time.time_ns()}__chatgpt__feat_out{VERSIONING_PREFIX}{VERSION_TO_USE}.json"

    for fname in SELECTED_PROMPT_PATH, SELECTED_PROMPT_CONT_PATH:
        ensure_file_versioning_ok(
            folder_to_check=PROMPT_FOLDER_LOCATION,
            versioning_prefix=VERSIONING_PREFIX,
            n_version_to_use=VERSION_TO_USE,
            selected_fname=fname,
            required_file_id_substr=PROMPT_FILE_ID_SUBSTR,
            FORCE_ACCEPT_NONMAX_VERSION=FORCE_ACCEPT_NONMAX_VERSION
        )

    if n_args == 1:
        run_chatgpt_behavioral_analysis(
            prompt_filepath=SELECTED_PROMPT_PATH,  # default system prompt file
            continuation_prompt_filepath=SELECTED_PROMPT_CONT_PATH,
            path_to_data=PATH_TO_CONV_DATA,
            response_writepath=RESPONSE_WRITEPATH,
            model="gpt-4o-2024-11-20",
            model_role="You are a call analysis system creating useful features to input to a scam detection model.", # default role we could use
            start_transcript_index=0,
            end_transcript_index=1
        )
    elif n_args == 2:
        run_chatgpt_behavioral_analysis(
            prompt_filepath=sys.argv[1],  # arg from cl
            continuation_prompt_filepath=SELECTED_PROMPT_CONT_PATH,
            path_to_data=PATH_TO_CONV_DATA,
            response_writepath=RESPONSE_WRITEPATH,
            model="gpt-4o-2024-11-20",
            model_role="You are a call analysis system creating useful features to input to a scam detection model.", # default role we could use
            start_transcript_index=0,
            end_transcript_index=1
        )
    elif n_args == 3:
        run_chatgpt_behavioral_analysis(
            prompt_filepath=sys.argv[1],  # arg from cl
            continuation_prompt_filepath=sys.argv[2], # arg from cl
            path_to_data=PATH_TO_CONV_DATA,
            response_writepath=RESPONSE_WRITEPATH,
            model="gpt-4o-2024-11-20",
            model_role="You are a call analysis system creating useful features to input to a scam detection model.", # default role we could use
            start_transcript_index=0,
            end_transcript_index=1
        )
