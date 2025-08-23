import os
import time
from collections import deque
from src.general_file_utils.utils.pkl import load_pkl, make_pkl_file, overwrite_pkl
from src.ml_scam_classification.utils.timestamps import is_unix_timestamp_ns

NS_PER_MINUTE = 60_000_000_000  # 60 seconds in ns

def _require(cond: bool, msg: str, err=ValueError):
    if not cond:
        raise err(msg)

def _rpm_from_filename_fast(filename: str) -> int:
    _require(filename.endswith(".pkl"), "Provided non-pkl log file (log file must be a .pkl)")
    j = len(filename) - 4
    i = filename.rfind("prev", 0, j)
    _require(i != -1, 'The logfile must end in "prev<rpm>.pkl" (e.g., "...prev60.pkl").')
    rpm_str = filename[i + 4 : j]
    _require(rpm_str.isdigit(), "Filename rpm must be digits, e.g., prev60.pkl")
    return int(rpm_str)

class RateLimiter:
    """
    Enforce an RPM limit with a persistent deque of ns timestamps.
    - Pickle file stores: deque[int] with maxlen=rpm.
    - Call .wait() immediately before your rate-limited action.
    - epsilon_s: small cushion (seconds) added only when sleeping.
    - requests_per_log_write: write the log to disk after this many requests.
    """

    __slots__ = (
        "rpm",
        "log_path",
        "print_updates",
        "_dq",
        "_requests_per_log_write",
        "_requests_since_log_write",
        "_epsilon_ns",
    )

    def __init__(
        self,
        rpm: int,
        log_path: str,
        *,
        create_pkl_w_deque: bool = False,
        print_updates: bool = True,
        requests_per_log_write: int = 1,
        epsilon_s: float = 0.001,  # 1 ms cushion
    ):
        _require(isinstance(rpm, int) and rpm > 0, "rpm (requests per minute) must be a positive int.")
        _require(isinstance(log_path, str), "log_path must be of type: str")

        directory, log_filename = os.path.split(log_path)
        directory = directory or "."
        _require(os.path.isdir(directory), f"Directory does not exist: {directory}")

        file_rpm = _rpm_from_filename_fast(log_filename)
        _require(file_rpm == rpm, "Passed rpm must match rpm in log filename")

        if not create_pkl_w_deque:
            _require(os.path.exists(log_path),
                     "log_path must exist. Please create the log first with create_pkl_w_deque=True.")

        _require(isinstance(print_updates, bool), "print_updates must be type: bool")
        _require(isinstance(requests_per_log_write, int) and requests_per_log_write >= 1,
                 "requests_per_log_write must be int >= 1")
        _require(isinstance(epsilon_s, (int, float)) and epsilon_s >= 0.0,
                 "epsilon_s must be a non-negative number")

        if create_pkl_w_deque:
            dq = deque(maxlen=rpm)
            dq.append(time.time_ns())
            make_pkl_file(path=log_path, data=dq)
        else:
            dq = load_pkl(log_path)
            _require(isinstance(dq, deque),
                     f"Loaded log pkl obj, but it was not a deque. Loaded from:\n{log_path}", err=TypeError)
            _require(dq.maxlen == rpm,
                     "Loaded log data deque from .pkl must have maxlen equal to rpm... log file is not correctly configured...")
            _require(all(is_unix_timestamp_ns(x) for x in dq),
                     "loaded log data deque from .pkl must contain only unix timestamps (ns).")

        self.rpm = rpm
        self.log_path = log_path
        self.print_updates = print_updates
        self._dq = dq
        self._requests_per_log_write = requests_per_log_write
        self._requests_since_log_write = 0
        self._epsilon_ns = int(epsilon_s * 1e9)

    def _write_log_if_needed(self):
        self._requests_since_log_write += 1
        if self._requests_since_log_write >= self._requests_per_log_write:
            overwrite_pkl(path=self.log_path, data=self._dq)
            self._requests_since_log_write = 0

    def wait(self):
        dq = self._dq
        now = time.time_ns()

        # Fast path: capacity not yet hit.
        if len(dq) < dq.maxlen:
            dq.append(now)
            self._write_log_if_needed()
            return

        # Full: ensure oldest is at least 60s old.
        oldest = dq[0]
        required_ns = (oldest + NS_PER_MINUTE) - now  # >0 means we must wait

        if required_ns > 0:
            # Add epsilon cushion *only when we must wait*.
            wait_ns = required_ns + self._epsilon_ns
            if self.print_updates:
                print(f"Waiting {wait_ns / 1e9:.6f} seconds to follow rate limits...")
            time.sleep(wait_ns / 1e9)

        dq.append(time.time_ns())
        self._write_log_if_needed()
