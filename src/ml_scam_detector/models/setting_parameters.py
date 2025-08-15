import inspect
from functools import wraps
from src.ml_scam_detector.models.meta_models import SingletonMeta

class AudioTranscriptionSettingsParameterIds(metaclass=SingletonMeta):  # Singleton settings class
    MAX_SUPPORTED_AUDIO_SIZE_BYTES: str = "MAX_AUD_BYTES"

audio_transcription_settings_parameter_ids = AudioTranscriptionSettingsParameterIds()

def validate_audio_transcription_settings(param_to_setting_map):
    """Decorator factory that maps function params to setting IDs and validates"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get bound arguments
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate each mapped parameter
            settings = audio_transcription_settings_parameter_ids
            for param_name, param_value in bound.arguments.items():
                if param_name in param_to_setting_map:
                    setting_id = param_to_setting_map[param_name]
                    valid_values = settings.VALID_SETTINGS.get(setting_id, [])
                    # TODO - settingchecker to check setting
                    
                    if valid_values and param_value not in valid_values:
                        raise ValueError(
                            f"Invalid value for {setting_id}. "
                            f"Got {param_value}, expected one of: {valid_values}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Usage
@map_params_audio_transcription_settings(SettingParameters().settings)
def process_user(user_id: int, session_token: str):
    """Now uses mapped parameter names internally"""
    print(f"Processing {user_id} with {session_token}")

# The decorator will convert parameters to their mapped names
process_user(123, "abc123")  # Internally uses settings-mapped names
