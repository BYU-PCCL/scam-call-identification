from typing import Tuple
from src.ml_scam_classification.settings.global_settings import global_settings
from src.ml_scam_classification.models.meta_models import SingletonMeta

class AudioTranscriptionMetaSettings(metaclass=SingletonMeta):
    # DEFAULT SETTING VALUES LISTED HERE
    min__min__max_supported_audio_size_bytes: int = 8000

# ADJUST THESE SETTINGS AS DESIRED
audio_transcription_meta_settings = AudioTranscriptionMetaSettings(
    min__min__max_supported_audio_size_bytes = 8000
)