from dataclasses import dataclass
from typing import List
from src.ml_scam_detector.models.meta_models import SingletonMeta

@dataclass
class SettingsPaths(metaclass=SingletonMeta):
    audio_transcription_settings_path: str

# ADJUST IF PATHS CHANGE
settings_paths = SettingsPaths(
    audio_transcription_settings_path = "src/ml_scam_detector/settings/audio_transcription_settings.json"
)

# ADJUST FOR DIFFERENT DESIRED SETTINGS
@dataclass
class GlobalSettings(metaclass=SingletonMeta):
    settings_paths = SettingsPaths()

    def __post_init__(self):
        # ensure settings within acceptable bounds
        pass


global_settings = GlobalSettings()