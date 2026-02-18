import pytest
from security_utils import validate_command, sanitize_path
import os

def test_validate_command_safe():
    assert validate_command("Help: Command=Help") == True
    assert validate_command("SelectAll") == True
    assert validate_command("GetInfo: Type=Tracks") == True

def test_validate_command_injection():
    # Attempting to use semicolon or quotes for injection
    assert validate_command("Help: Command=Help; Export: Filename=\"/etc/passwd\"") == False
    assert validate_command("Export: Filename=\"/tmp/test.wav\"") == False # Not in SAFE_COMMANDS

def test_sanitize_path_traversal():
    base = "/home/user/workspace"
    assert sanitize_path("file.wav", base) == os.path.join(base, "file.wav")
    assert sanitize_path("../etc/passwd", base) == None
    assert sanitize_path("subdir/../../etc/passwd", base) == None
