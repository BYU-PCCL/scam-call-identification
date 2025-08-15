from typing import Union, List
from pydub import AudioSegment
from src.ml_scam_detector.utils.file_models import AudioFilePath, DirPath, FileExtension, NonEmptyDir, JSONFilePath, DirPathAlwaysRequireExists

from pydub.utils import mediainfo
from src.ml_scam_detector.utils.json_utils import get_json_from_path_str
from src.ml_scam_detector.utils.enforce_fn_properties import (
    enforce_types,
    ensure_list_param_not_empty,
    ensure_valid_audio_conversion_settings
)
from src.ml_scam_detector.utils.file_utils import (
    assert_folder_has_at_least_one_file,
    assert_path_exists,
    folder_only_has_given_file_types,
    assert_filepath_is_audio_file,
    get_paths_to_all_files_in_folder,
    get_file_extension_from_path_str
)


def get_supported_transcription_model_str_ids():
    supported_transcription_models_info_json = get_json_from_path_str(
        path=JSONFilePath("src/ml_scam_detector/settings/supported_transcription_models.json"),
        context="In get_supported_transcription_model_str_idx"
    )
    list_supported_models_entries = None

    def raise_err():
        raise KeyError("Attempted to access supoprted transcription models - key error")

    try:
        list_supported_models_entries = supported_transcription_models_info_json["supported_transcription_models"]
    except:
        raise_err()
    
    list_supported_model_ids = None
    try:
        for supported_model_entry in list_supported_models_entries:
            list_supported_model_ids.append(supported_model_entry["transcription_model_id_string"])
    except:
        raise_err()

    return list_supported_model_ids


def assert_transcription_model_is_supported(model):
    supported_transcription_model_ids = get_supported_transcription_model_str_ids()
    if model not in supported_transcription_model_ids:
        raise ValueError(f"Attempted to use non-supported transcription model: {model}. \
                         Supported models: {supported_transcription_model_ids}")


def get_audio_format(path_to_audio_file):
    info = mediainfo(path_to_audio_file)
    audio_format = info['format_name']  # e.g., 'mp3', 'wav', etc.
    return audio_format


@enforce_types
@ensure_list_param_not_empty("supported_sampling_rates")
def change_audio_sample_rate_preserve_max_info(
        path_to_input_audio_file: AudioFilePath,
        path_to_output_dir: DirPath,
        supported_sampling_rates: List[int],
        any_sampling_rate_supported: False,
        ensure_input_audio_file_exists: bool = True,
        create_output_dir: bool = False # If False, output dir must exist
):


@enforce_types
def convert_audio_object_to_supported_sampling_rate(
        path_to_input_audio_file: DirPathAlwaysRequireExists,
        path_to_output_dir: DirPath,
        supported_sampling_rates: List[int],
        any_sampling_rate_supported: False,
        ensure_input_audio_file_exists: bool = True,
        create_output_dir: bool = False, # If False, output dir must exist
        err_context = "In convert_audio_object_to_supported_sampling_rate"
):
    
    audio = AudioSegment.from_file(input_audio_file_path)
    new_sampling_rate = 16000 if audio.frame_rate > 8000 else 8000
    audio = audio.set_frame_rate(new_sampling_rate)

    # temporarily store audio file w/new sampling rate (same file format) in a folder
    audio_format = get_audio_format(input_audio_file_path)
    audio.export("output.wav", format=audio_format)


@enforce_types
def transcribe_audio_file(
        input_audio_file_path: AudioFilePath,
        output_text_dirpath: DirPath,
        max_supported_file_size_bytes: int,
        supported_sampling_rates: Union[List[int]],
        any_sampling_rate_supported: bool = False, # must explicitly set to true to allow supported_sampling_rates to be empty
        model: str = get_supported_transcription_model_str_ids[0],
        prompt: Union[str, None] = None,
        per_file_transcripts_folder_suffix: str = "_transcription",
        transcript_file_suffix: str = "_transcription_pt"
    ):
    # ensure chose supported model
    assert_transcription_model_is_supported(model)

    # supported_sampling_rates value and any_sampling_rate_supported value must match
    # (this is a double-check to ensure any format supported is the desired setting)
    context = "In transcribe_audio_file - conflicting args:"


    #  _____________________________________________________________
    # |     CONVERT TO EXPECTED FORMAT FOR TRANSCRIPTION MODEL      |
    # |_____________________________________________________________|
    # Need to segment audio to reduce to file size supported by audio transcription model
    # using Silero VAD DNN to find non-word pauses to avoid clipping words

    # Silero VAD (using to identify non-speech pauses) supports 8000 Hz and 16000 Hz sampling rates
    
    # Convert <= 8000 Hz files to 8000 Hz, and > 8000 Hz to 16000 to preserve as much audio information as possible
    convert_audio_to_supported_sampling_rate
    audio = AudioSegment.from_file(input_audio_file_path)
    new_sampling_rate = 16000 if audio.frame_rate > 8000 else 8000
    audio = audio.set_frame_rate(new_sampling_rate)

    # temporarily store audio file w/new sampling rate (same file format) in a folder
    audio_format = get_audio_format(input_audio_file_path)
    audio.export("output.wav", format=audio_format)

    # --- COMPUTE SEGMENT BOUNDARY LOCATIONS ---
    #           Segments must be less than the 25 MB limit required by OpenAI Whisper transcription model
    #           Cutting off words will mess up transcription, so using Silero VAD to ensure audio is clipped between words
    
    # compute rough segment boundary timestamps (may change if a word would be cut off)


    # For each rough segment boundary, find midpoint timestamp of the 30ms non-voice audio segment closest to the segment boundary

    # --- SEGMENT AUDIO FILE INTO CHUNKS ---
    # segment audio file into chunks based on finalized segment boundaries in temp folder for transcription

    #  _____________________________________________________________
    # |          TRANSCRIBE AUDIO AND STORE TRANSCRIPTS             |
    # |_____________________________________________________________|

    # --- TRANSCRIBE EACH CHUNK AND 
    # transcribe each chunk and write to folder


@enforce_types
@ensure_list_param_not_empty("supported_file_extensions")
@ensure_valid_audio_conversion_settings
def transcribe_audio_clips_in_folder(
        input_folder_path: NonEmptyDir,
        output_folder_path: DirPath,
        supported_file_extensions: List[FileExtension],
        max_supported_file_size_bytes: int,
        supported_sampling_rates: Union[List[int]],
        any_sampling_rate_supported: bool = False, # must explicitly set to true to allow supported_sampling_rates to be empty
        model: str = get_supported_transcription_model_str_ids[0],
        prompt: Union[str, None] = None,
        per_file_transcripts_folder_suffix: str = "_transcription",
        transcript_file_suffix: str = "_transcription_pt",
        ignore_non_supported_files: bool = False
):
    # If not ignoring non-supported files - ensure input folder contains only file extensions to convert
    if not ignore_non_supported_files:
        if not folder_only_has_given_file_types(
            folder_path=input_folder_path,
            allowed_types=supported_file_extensions,
            input_folder_path=input_folder_path,
            supported_file_extensions=supported_file_extensions,
            ignore_non_supported_files=ignore_non_supported_files
            ):
            raise ValueError(f"Could not transcribe audio files in: {input_folder_path} - encountered unsupported file extensions with ignore_non_supported_files=False")

    # Make sure all (non-ignored) files in folder are audio files
    filepaths_files_attempting_to_convert=[]
    for filepath in get_paths_to_all_files_in_folder(input_folder_path):
        if get_file_extension_from_path_str(filepath) in supported_file_extensions or not ignore_non_supported_files:
            # filepath deemed to be supported (or we aren't ignoring any files and trying to convert them all)
            filepaths_files_attempting_to_convert.append(filepath)

    for filepath in filepaths_files_attempting_to_convert:
        # need to make sure its an audio file, as it will be converted
        assert_filepath_is_audio_file(filepath)

    for filepath in filepaths_files_attempting_to_convert:
        # can actually convert now
        transcribe_audio_file(filepath, output_folder_path)
        break


if __name__ == "__main__":
    transcribe_audio_clips_in_folder(
        input_folder_path="src/ml_scam_detector/data/real-phone-calls/josearangos_spanish-calls-corpus-Friends/calls_audio",
        output_folder_path="src/ml_scam_detector/data/real-phone-calls/josearangos_spanish-calls-corpus-Friends/calls_transcripts",
        supported_file_extensions=["wav"],
        ignore_non_supported_files=False
    )
    