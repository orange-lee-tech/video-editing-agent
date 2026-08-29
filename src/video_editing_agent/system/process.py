from __future__ import annotations

import os
import subprocess


def external_process_creationflags() -> int:
    """Hide child console windows for CLI tools launched by the Windows GUI.

    stdout/stderr capture and exit codes remain unchanged. POSIX receives zero,
    which preserves ordinary subprocess behavior.
    """

    if os.name != "nt":
        return 0
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
