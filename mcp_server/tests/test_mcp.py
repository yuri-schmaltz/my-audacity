import pytest
import os
import unittest.mock as mock
from mcp_audacity import _send_command

@mock.patch('os.path.exists')
@mock.patch('builtins.open', new_callable=mock.mock_open, read_data="Track1\nTrack2\n\n")
def test_send_command_success(mock_open, mock_exists):
    # Setup mocks
    mock_exists.return_value = True
    
    # Run test
    result = _send_command("GetInfo: Type=Tracks")
    
    # Assertions
    assert "Track1" in result
    assert "Track2" in result
    mock_open.assert_any_call(mock.ANY, 'w')
    mock_open.assert_any_call(mock.ANY, 'r')

@mock.patch('os.path.exists')
def test_send_command_no_pipes(mock_exists):
    # Setup mocks
    mock_exists.return_value = False
    
    # Run test
    result = _send_command("Help")
    
    # Assertions
    assert "Error: Audacity pipes not found" in result

@mock.patch('os.path.exists')
@mock.patch('builtins.open', side_exception=IOError("Pipe error"))
def test_send_command_io_error(mock_open, mock_exists):
    # Setup mocks
    mock_exists.return_value = True
    
    # Run test
    # Note: _send_command catches exceptions and returns error string
    result = _send_command("Help")
    
    # Assertions
    assert "Error communicating with Audacity" in result
