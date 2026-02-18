import os
import sys
import json
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audacity-mcp")

# Initialize FastMCP server
mcp = FastMCP("Audacity")

# Platform specific constants
if sys.platform == 'win32':
    WRITE_NAME = '\\\\.\\pipe\\ToSrvPipe'
    READ_NAME = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    # Linux or Mac
    PIPE_BASE = '/tmp/audacity_script_pipe.'
    WRITE_NAME = PIPE_BASE + 'to.' + str(os.getuid())
    READ_NAME = PIPE_BASE + 'from.' + str(os.getuid())
    EOL = '\n'

def _send_command(command: str) -> str:
    """Internal helper to send a command to Audacity and read response."""
    if not os.path.exists(WRITE_NAME) or not os.path.exists(READ_NAME):
        return "Error: Audacity pipes not found. Is Audacity running with mod-script-pipe enabled?"

    try:
        with open(WRITE_NAME, 'w') as to_pipe:
            logger.info(f"Sending command: {command}")
            to_pipe.write(command + EOL)
            to_pipe.flush()

        with open(READ_NAME, 'r') as from_pipe:
            response = ""
            while True:
                line = from_pipe.readline()
                if line == '\n' and len(response) > 0:
                    break
                response += line
            return response.strip()
    except Exception as e:
        logger.error(f"Error communicating with Audacity: {e}")
        return f"Error communicating with Audacity: {e}"

@mcp.tool()
def audacity_command(command: str) -> str:
    """
    Send a raw scripting command to Audacity.
    
    Examples:
    - 'Help: Command=Help'
    - 'GetInfo: Type=Tracks'
    - 'SelectAll'
    - 'Export: Filename="/tmp/test.wav"'
    """
    return _send_command(command)

@mcp.tool()
def get_track_info() -> str:
    """Get information about all tracks in the current project."""
    return _send_command("GetInfo: Type=Tracks")

@mcp.tool()
def list_available_commands() -> str:
    """List all available scripting commands in Audacity."""
    return _send_command("Help: Command=Help")

if __name__ == "__main__":
    mcp.run()
