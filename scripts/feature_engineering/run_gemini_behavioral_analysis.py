import sys
import time
import os

from src.llm_tools.gemini_feature_extraction import run_gemini_behavioral_analysis
from src.ml_scam_classification.utils.file_utils import ensure_file_versioning_ok

# Project-specific rate limit object (blocks via rl.wait() inside Gemini calls)
from settings.rate_limits.llms.gemini.pro_2_5 import GEMINI_2_5_PRO_5RPM as GEMINI_RL


if __name__ == "__main__":
    # SETTINGS
    PROMPT_FOLDER_LOCATION = "src/ml_scam_classification/prompting"
    VERSION_TO_USE = 7
    VERSIONING_PREFIX = "_v"
    SELECTED_PROMPT_PATH = f"{PROMPT_FOLDER_LOCATION}/prompt_conner{VERSIONING_PREFIX}{VERSION_TO_USE}.txt"

    ######## MASTER SETTINGS - careful when adjusting these as they may have filesystem implications
    PROMPT_FILE_ID_SUBSTR = "prompt"  # Assuming all prompt files contain kw: "prompt" somewhere in filename
    FORCE_ACCEPT_NONMAX_VERSION = False  # Will prompt user to double-check if set to true

    ensure_file_versioning_ok(
        folder_to_check=PROMPT_FOLDER_LOCATION,
        versioning_prefix=VERSIONING_PREFIX,
        n_version_to_use=VERSION_TO_USE,
        selected_fname=SELECTED_PROMPT_PATH,
        required_file_id_substr=PROMPT_FILE_ID_SUBSTR,
        FORCE_ACCEPT_NONMAX_VERSION=FORCE_ACCEPT_NONMAX_VERSION,
    )

    def mk_output_path() -> str:
        p = f"outputs/{time.time_ns()}__feature_extraction_out{VERSIONING_PREFIX}{VERSION_TO_USE}.json"
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        return p

    n_args = len(sys.argv)

    if n_args == 1:
        run_gemini_behavioral_analysis(
            prompt_filepath=SELECTED_PROMPT_PATH,
            response_writepath=mk_output_path(),
            rl=GEMINI_RL,  # <-- pass the rate limiter
        )
    elif n_args == 2:
        run_gemini_behavioral_analysis(
            prompt_filepath=sys.argv[1],
            response_writepath=mk_output_path(),
            rl=GEMINI_RL,  # <-- pass the rate limiter
        )
    elif n_args == 3:
        run_gemini_behavioral_analysis(
            prompt_filepath=sys.argv[1],
            response_writepath=sys.argv[2],
            rl=GEMINI_RL,  # <-- pass the rate limiter
        )
    else:
        raise ValueError("Usage: script.py [<path_to_prompt>] [<response_writepath>]")
