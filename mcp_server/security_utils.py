import os
import re
from typing import Optional

# Allowlist of safe command verbs in Audacity
# Only commands that don't involve arbitrary file paths or destructive system actions
SAFE_COMMANDS = {
    "Help", "GetInfo", "SelectAll", "SelectNone", "Play", "Stop", "Pause",
    "Record", "Undo", "Redo", "SetTrack", "GetTrackVisualState"
}

# Regex to validate basic command structure: Verb: Key=Value Key=Value
# Or just a Verb
COMMAND_REGEX = re.compile(r"^[A-Za-z0-9]+(:[ \t]*[A-Za-z0-9]+=[^;\"\']+)*$")

def validate_command(command: str) -> bool:
    """
    Validates if a command is safe to execute.
    Currently checks against a basic regex. 
    Enhanced version would check against an allowlist of Verbs.
    """
    if not command or not isinstance(command, str):
        return False
    
    verb = command.split(":")[0].strip()
    if verb not in SAFE_COMMANDS and ":" in command:
        # If it has parameters, we are extra careful
        return False
    
    return bool(COMMAND_REGEX.match(command))

def sanitize_path(path: str, base_dir: str) -> Optional[str]:
    """
    Ensures a path is within the base_dir and prevents traversal.
    """
    abs_base = os.path.abspath(base_dir)
    abs_target = os.path.abspath(os.path.join(abs_base, path))
    
    if os.path.commonpath([abs_base, abs_target]) == abs_base:
        return abs_target
    return None
