import sys
import time
import os

from src.llm_tools.chatgpt_feature_extraction import run_chatgpt_behavioral_analysis
from src.ml_scam_classification.utils.file_utils import ensure_file_versioning_ok

# 🔒 Rate limit object (placeholder import; point this to your real settings module)
# e.g., define GPT4O_15RPM in settings/ratelimits.py using your RateLimiter class
from settings.rate_limits.llms.chatgpt.GPT_5 import GPT_5_10RPM


if __name__ == "__main__":
    # Validate CLI args
    n_args = len(sys.argv)
    if n_args > 3:
        raise ValueError("Too many arguments. usage: script.py <path_to_prompt>(opt.) <path_to_continuation_prompt>(opt.)")

    # SETTINGS
    PROMPT_FOLDER_LOCATION = "src/ml_scam_classification/prompting"
    VERSION_TO_USE = 7
    VERSIONING_PREFIX = "_v"
    SELECTED_PROMPT_PATH = (
        f"src/ml_scam_classification/prompting/prompt_conner{VERSIONING_PREFIX}{str(VERSION_TO_USE)}.txt"
        if n_args < 2 else sys.argv[1]
    )
    SELECTED_PROMPT_CONT_PATH = (
        f"src/ml_scam_classification/prompting/prompt_conner{VERSIONING_PREFIX}{str(VERSION_TO_USE)}_contd.txt"
        if n_args < 3 else sys.argv[2]
    )
    PATH_TO_CONV_DATA = "src/ml_scam_classification/data/call_data_by_conversation/raw_data/call_data_by_conversation_conv_only.csv"

    ######## MASTER SETTINGS - careful when adjusting these as they may have filesystem implications
    PROMPT_FILE_ID_SUBSTR = "prompt"  # Assuming all prompt files contain kw: "prompt" somewhere in filename
    FORCE_ACCEPT_NONMAX_VERSION = False  # prompt user to double-check?
    RESPONSE_WRITEPATH = f"outputs/{time.time_ns()}__chatgpt__feat_out{VERSIONING_PREFIX}{str(VERSION_TO_USE)}.json"

    # Ensure output dir exists
    os.makedirs(os.path.dirname(RESPONSE_WRITEPATH) or ".", exist_ok=True)

    # Verify selected prompt files align with versioning policy
    for fname in (SELECTED_PROMPT_PATH, SELECTED_PROMPT_CONT_PATH):
        ensure_file_versioning_ok(
            folder_to_check=PROMPT_FOLDER_LOCATION,
            versioning_prefix=VERSIONING_PREFIX,
            n_version_to_use=VERSION_TO_USE,
            selected_fname=fname,
            required_file_id_substr=PROMPT_FILE_ID_SUBSTR,
            FORCE_ACCEPT_NONMAX_VERSION=FORCE_ACCEPT_NONMAX_VERSION,
        )

    # Run with required rate limiter (GPT_5_10RPM). The function will call rl.wait() internally.
    if n_args == 1:
        run_chatgpt_behavioral_analysis(
            prompt_filepath=SELECTED_PROMPT_PATH,
            continuation_prompt_filepath=SELECTED_PROMPT_CONT_PATH,
            path_to_data=PATH_TO_CONV_DATA,
            response_writepath=RESPONSE_WRITEPATH,
            model="gpt-4o-2024-11-20",
            model_role="You are a call analysis system creating useful features to input to a scam detection model.",
            rl=GPT_5_10RPM,  # <-- pass RL
            start_transcript_index=0,
            end_transcript_index=1,
        )
    elif n_args == 2:
        run_chatgpt_behavioral_analysis(
            prompt_filepath=sys.argv[1],
            continuation_prompt_filepath=SELECTED_PROMPT_CONT_PATH,
            path_to_data=PATH_TO_CONV_DATA,
            response_writepath=RESPONSE_WRITEPATH,
            model="gpt-4o-2024-11-20",
            model_role="You are a call analysis system creating useful features to input to a scam detection model.",
            rl=GPT_5_10RPM,  # <-- pass RL
            start_transcript_index=0,
            end_transcript_index=1,
        )
    elif n_args == 3:
        run_chatgpt_behavioral_analysis(
            prompt_filepath=sys.argv[1],
            continuation_prompt_filepath=sys.argv[2],
            path_to_data=PATH_TO_CONV_DATA,
            response_writepath=RESPONSE_WRITEPATH,
            model="gpt-4o-2024-11-20",
            model_role="You are a call analysis system creating useful features to input to a scam detection model.",
            rl=GPT_5_10RPM,  # <-- pass RL
            start_transcript_index=0,
            end_transcript_index=1,
        )
