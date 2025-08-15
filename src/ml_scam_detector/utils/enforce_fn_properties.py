import functools
import inspect


def enforce_types(fn):
    sig = inspect.signature(fn)
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            expected_type = fn.__annotations__.get(name)
            if expected_type and not isinstance(value, expected_type):
                raise TypeError(
                    f"Argument '{name}' must be of type '{expected_type.__name__}', got '{type(value).__name__}'"
                )
        return fn(*args, **kwargs)
    return wrapper


import inspect
import functools

def enforce_types_disallow_none(fn):
    """
    Decorator to enforce:
      1. No argument may be None.
      2. Each argument matches the annotated type on the function.
    """
    sig = inspect.signature(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for name, value in bound.arguments.items():
            # 1) Disallow None for any parameter
            if value is None:
                raise TypeError(f"Argument '{name}' must not be None")

            # 2) Enforce annotated types
            expected_type = fn.__annotations__.get(name)
            if expected_type and not isinstance(value, expected_type):
                raise TypeError(
                    f"Argument '{name}' must be of type "
                    f"'{expected_type.__name__}', got '{type(value).__name__}'"
                )

        return fn(*args, **kwargs)

    return wrapper



def ensure_list_param_not_empty(param_name):
    def decorator(fn):
        sig = inspect.signature(fn)
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            value = bound.arguments.get(param_name)
            if not isinstance(value, list):
                raise ValueError(f"Argument '{param_name}' must be a list, got {type(value).__name__}")
            if len(value) == 0:
                raise ValueError(f"Argument '{param_name}' must not be an empty list")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def ensure_valid_audio_conversion_settings(fn):
    sig = inspect.signature(fn)
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        supported_sampling_rates = bound.arguments.get("supported_sampling_rates")
        any_sampling_rate_supported = bound.arguments.get("any_sampling_rate_supported")
        err_context = bound.arguments.get("err_context")
        max_supported_file_size_bytes = bound.arguments.get("max_supported_file_size_bytes")

        # Ensure valid sampling rate settings
        if len(supported_sampling_rates) == 0 and not any_sampling_rate_supported:
            raise ValueError(f"{err_context} Passed empty supported_sampling_rates list, but did not set any_sampling_rate_supported...")
        else:
            if any_sampling_rate_supported:
                # passed supported sampling rates and attempted to allow any sampling rate - conflicting arguments
                raise ValueError(f"{err_context} Passed supported_sampling_rates list and attempted to set any_sampling_rate_supported to True...")
        
        # Ensure fn parameters adhere to audio transcriptions settings
        fn_name = fn.__name__
        


        return fn(*args, **kwargs)
    return wrapper
