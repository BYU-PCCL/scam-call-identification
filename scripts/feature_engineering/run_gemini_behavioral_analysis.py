import sys
import time

from src.llm_tools.gemini_feature_extraction import run_gemini_behavioral_analysis
from src.ml_scam_classification.utils.file_utils import ensure_file_versioning_ok

if __name__ == "__main__":
    # SETTINGS
    PROMPT_FOLDER_LOCATION = "src/ml_scam_classification/prompting"
    VERSION_TO_USE = 7
    VERSIONING_PREFIX = "_v"
    SELECTED_PROMPT_PATH = f"src/ml_scam_classification/prompting/prompt_conner{VERSIONING_PREFIX}{str(VERSION_TO_USE)}.txt"

    ######## MASTER SETTINGS - careful when adjusting these as they may have filesystem implications
    PROMPT_FILE_ID_SUBSTR = "prompt" # Assuming all prompt files contain kw: "prompt" somewhere in filename
    FORCE_ACCEPT_NONMAX_VERSION = False # Will prompt user to double-check if set to true

    ensure_file_versioning_ok(
        folder_to_check=PROMPT_FOLDER_LOCATION,
        versioning_prefix=VERSIONING_PREFIX,
        n_version_to_use=VERSION_TO_USE,
        selected_fname=SELECTED_PROMPT_PATH,
        required_file_id_substr=PROMPT_FILE_ID_SUBSTR,
        FORCE_ACCEPT_NONMAX_VERSION=FORCE_ACCEPT_NONMAX_VERSION
    )

    n_args = len(sys.argv)
    if n_args == 1:
        run_gemini_behavioral_analysis(
            prompt_filepath=SELECTED_PROMPT_PATH,
            response_writepath=f"outputs/{time.time_ns()}__feature_extraction_out{VERSIONING_PREFIX}{str(VERSION_TO_USE)}.json"
            )
    elif n_args == 2:
        run_gemini_behavioral_analysis(sys.argv[1])
        run_gemini_behavioral_analysis(
            prompt_filepath=sys.argv[1],
            response_writepath=f"outputs/{time.time_ns()}__feature_extraction_out{VERSIONING_PREFIX}{str(VERSION_TO_USE)}.json"
            )
    elif n_args == 3:
        run_gemini_behavioral_analysis(sys.argv[1], sys.argv[2])
