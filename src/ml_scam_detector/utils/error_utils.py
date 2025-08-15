import inspect
from functools import wraps

def format_context(fn):
    """
    Decorator that ensures the wrapped function is called with a 'context' argument.
    If so, appends a space to its value before invocation.
    Otherwise, raises a TypeError.
    """
    sig = inspect.signature(fn)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Bind the passed args/kwargs to the function's signature
        try:
            bound = sig.bind(*args, **kwargs)
        except TypeError as e:
            # Missing required positional or unexpected argument
            raise

        arguments = bound.arguments

        # Check for 'context'
        if 'context' not in arguments:
            raise TypeError(f"{fn.__name__}() missing required argument: 'context'")

        # Modify it in-place: append a space
        original_context = arguments['context']
        if not isinstance(original_context, str):
            raise TypeError(f"{fn.__name__}() expected 'context' to be str, got {type(original_context).__name__}")
        arguments['context'] = "" if not original_context else original_context + " -"

        # Call the original function with the modified arguments
        return fn(**arguments)

    return wrapper
