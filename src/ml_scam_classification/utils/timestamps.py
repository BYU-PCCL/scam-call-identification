import time

def is_unix_timestamp_ns(value):
    if not isinstance(value, int):
        return False
    # Check if within plausible range for nanoseconds since 1970 (e.g., from 1970 to 3000)
    # Current timestamp_ns around 1.7e18, 3000 years after epoch ~ 3e19
    return 1_000_000_000_000_000_000 <= value <= 3_000_000_000_000_000_000

# Example usage:
ts = time.time_ns()
print(is_unix_timestamp_ns(ts))  # True
