import os
import re
import time
from collections import deque
from src.general_file_utils.utils.pkl import load_pkl, make_pkl_file, overwrite_pkl
from src.ml_scam_classification.utils.timestamps import is_unix_timestamp_ns

NS_PER_MINUTE = 60_000_000_000  # 60 seconds in ns (integer math)

# small stdlib-only helper to avoid repeated if/raise blocks
def require(cond: bool, msg: str, err=ValueError):
    if not cond:
        raise err(msg)

def _rpm_from_filename(filename: str) -> int:
    """
    attempt to parse rpm number from log filename
    The logfile must end in "prev<rpm>.pkl" in order to ensure labels match rpm rule.
    """
    m = re.search(r'prev(\d+)\.pkl$', filename)
    require(m is not None, 'The logfile must end in "prev<rpm>.pkl" (e.g., "...prev60.pkl").')
    return int(m.group(1))

def wait_to_follow_rate_limits(
        rpm=None,
        OVERRIDE_MANUAL_CONFIRM=False,
        log_path=None,
        CREATE_LOG_OBJ=False,
        print_updates=True
):
    # Attempted to respect rate limits, but did not configure rpm value (found to be None)
    require(rpm is not None, "Attempted to respect rate limits, but did not configure rpm value (found to be None)")
    # OVERRIDE_MANUAL_CONFIRM must be type: bool
    require(isinstance(OVERRIDE_MANUAL_CONFIRM, bool), "OVERRIDE_MANUAL_CONFIRM must be type: bool")
    # rpm (requests per minute) must be an int.
    require(isinstance(rpm, int), "rpm (requests per minute) must be an int.")
    # CREATE_LOG_OBJ must be a bool.
    require(isinstance(CREATE_LOG_OBJ, bool), "CREATE_LOG_OBJ must be a bool.")
    # print_updates must be type: bool
    require(isinstance(print_updates, bool), "print_updates must be type: bool")
    # log_path must be of type: str
    require(isinstance(log_path, str), "log_path must be of type: str")

    need_existing_pkl = not CREATE_LOG_OBJ

    # ensure log file is a .pkl file
    log_filename = os.path.basename(log_path)
    require(log_filename.endswith('.pkl'), "Provided non-pkl log file (log file must be a .pkl)")

    # directory must exist (to hold the pkl)
    directory = os.path.dirname(log_path) or "."
    require(os.path.isdir(directory), f"Directory does not exist: {directory}")

    # should be one integer in the log filename, and should match the passed rpm
    file_rpm = _rpm_from_filename(log_filename)

    # rpm in filename must match passed rpm
    require(file_rpm == rpm, "Passed rpm must match rpm in log filename")

    if need_existing_pkl:
        # log_path must exist when using an existing log
        require(
            os.path.exists(log_path),
            "log_path must exist. Passed non-existent log path:\n"
            f"{log_path}\n"
            "Please create the log, ensuring to put the rpm number in the filename "
            "(to ensure there is a separate log for every rpm rule)"
        )

        # attempt to load pkl
        try:
            log_data_obj = load_pkl(log_path)
        except Exception as e:
            raise Exception("Failed to load pkl file") from e

        # pkl obj must be a deque
        require(isinstance(log_data_obj, deque),
                f"Loaded log pkl obj, but it was not a deque. Loaded from:\n{log_path}",
                err=TypeError)

        # pkl obj deque must be of unix timestamps
        require(all(is_unix_timestamp_ns(x) for x in log_data_obj),
                "loaded log data deque from .pkl must contain only unix timestamps (ns).")

        # pkl obj deque must have maxlen be equal to the rpm limit
        require(log_data_obj.maxlen == rpm,
                "Loaded log data deque from .pkl must have maxlen equal to rpm... log file is not correctly configured...")

        # if pkl obj deque not the length of the rpm req, means we have not made enough
        # requests to ever hit the rpm restriction, so we can make the request right away with no delay.
        if len(log_data_obj) < rpm:
            log_data_obj.append(time.time_ns())
            overwrite_pkl(path=log_path, data=log_data_obj)
            # now, we can return immediately so that the action with the rate limit (e.g. API call) can be completed
            return

        # If made it here, pkl obj is the length of the rpm req
        # See if a delay is needed (i.e. if the action n actions ago, with n being the rpm, was more than a minute ago)
        now = time.time_ns()
        oldest_appended_timestamp = log_data_obj[0]
        time_elapsed_beyond_min_req = now - oldest_appended_timestamp - NS_PER_MINUTE

        if not (time_elapsed_beyond_min_req > 0):
            # we haven't waited a minute since the request that previously caused us to hit the rpm limit
            # we must wait
            ns_to_wait = -time_elapsed_beyond_min_req
            s_to_wait = (ns_to_wait / 1e9) + 1  # add extra second to be safe

            if print_updates:
                print(f"Waiting {s_to_wait} seconds to follow rate limits...")

            time.sleep(s_to_wait)

            # add entry for this action, will displace older entries which cannot factor into rpm req
            # (due to entry idx >= rpm)
            log_data_obj.append(time.time_ns())

            # save pkl file with new entry
            overwrite_pkl(path=log_path, data=log_data_obj)

            # we've waited at least a minute since making our final request which previously hit the rpm limit
            # we can safely proceed with the action now
            return

        # no wait needed; record and persist
        log_data_obj.append(time.time_ns())
        overwrite_pkl(path=log_path, data=log_data_obj)
        # now, we can return immediately so that the action with the rate limit (e.g. API call) can be completed
        return

    else:
        # need to create pkl file and add the initial entry for this action
        # this is the first request, so no delay is needed
        dq = deque(maxlen=rpm)
        dq.append(time.time_ns())
        make_pkl_file(path=log_path, data=dq)
        # now, we can return immediately so that the action with the rate limit (e.g. API call) can be completed
        return
