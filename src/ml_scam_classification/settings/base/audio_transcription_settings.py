from dataclasses import dataclass
from src.ml_scam_classification.models.meta_models import SingletonMeta
from src.ml_scam_classification.settings.meta.audio_transcription_meta_settings import audio_transcription_meta_settings

@dataclass
class AudioTranscriptionSettings(metaclass=SingletonMeta):
    min_val_for_max_supported_audio_size_bytes: int

    def __post_init__(self):
        # ensure valid settings
        meta_setting_1 = audio_transcription_meta_settings.min__min__max_supported_audio_size_bytes
        if self.min_val_for_max_supported_audio_size_bytes < meta_setting_1:
            raise ValueError(f"Audio Transcription Setting: min_val_for_max_supported_audio_size_bytes invalid based on meta setting min__min__max_supported_audio_size_bytes: {meta_setting_1}")


# Singleton instance - ADJUST SETTINGS HERE
audio_transcription_settings = AudioTranscriptionSettings(
    min_val_for_max_supported_audio_size_bytes=8000
)
