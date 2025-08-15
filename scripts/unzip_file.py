#!/usr/bin/env python3
"""
unzip_runner.py

Usage:
  # 1) No arguments → use all defaults
  $ ./unzip_runner.py

  # 2) Exactly three args → use them (SRC_ZIP_PATH, DEST_DIR, DELETE_ZIPPED_FILE)
  $ ./unzip_runner.py /tmp/archive.zip /tmp/output true

If you supply any args, you must supply all three. Mixing defaults and CLI inputs is disallowed.
"""

import sys
from src.ml_scam_classification.utils.file_utils import unzip_file

# ─── Default configuration ────────────────────────────────────────────────

DEFAULT_SRC_ZIP_PATH     = '/path/to/archive.zip'
DEFAULT_DEST_DIR         = '/path/to/output/dir'
DEFAULT_DELETE_ZIPPED    = False  # Boolean

# ─── Helpers ──────────────────────────────────────────────────────────────

def parse_bool(val: str) -> bool:
    """Convert a string to bool, raising ValueError on bad input."""
    v = val.strip().lower()
    if v in ('true', '1', 'yes', 'y'):
        return True
    if v in ('false', '0', 'no', 'n'):
        return False
    raise ValueError(f"Invalid boolean value: '{val}' (expected true/false)")

# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args:
        # Use all defaults
        src_path, dest_dir, delete_zipped = (
            DEFAULT_SRC_ZIP_PATH,
            DEFAULT_DEST_DIR,
            DEFAULT_DELETE_ZIPPED
        )
    elif len(args) == 3:
        # Override all from CLI
        src_path      = args[0]
        dest_dir      = args[1]
        try:
            delete_zipped = parse_bool(args[2])
        except ValueError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(
            "❌ Invalid invocation. Either:\n"
            "    • No arguments  (→ use all defaults), or\n"
            "    • Exactly three arguments:\n"
            "        unzip_runner.py <SRC_ZIP_PATH> <DEST_DIR> <DELETE_ZIPPED_FILE>\n"
            "      where DELETE_ZIPPED_FILE is true|false\n",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        result_dir = unzip_file(
            src_path=src_path,
            dest_dir=dest_dir,
            delete_zipped_file=delete_zipped
        )
        print(f"✅ Successfully extracted archive to: {result_dir}")
    except Exception as e:
        print(f"❌ Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
