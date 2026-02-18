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

from metrics import track_performance, metrics
from security_utils import validate_command
import time

# Platform specific constants and logging paths
if sys.platform == 'win32':
    WRITE_NAME = '\\\\.\\pipe\\ToSrvPipe'
    READ_NAME = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
    LOG_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'Audacity', 'Logs')
else:
    # Linux or Mac
    PIPE_BASE = '/tmp/audacity_script_pipe.'
    WRITE_NAME = PIPE_BASE + 'to.' + str(os.getuid())
    READ_NAME = PIPE_BASE + 'from.' + str(os.getuid())
    EOL = '\n'
    # Use XDG_CACHE_HOME or ~/.cache for logs according to framework
    LOG_DIR = os.path.join(os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache')), 'audacity-mcp')

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)
if sys.platform != 'win32':
    os.chmod(LOG_DIR, 0o700) # Restrict log directory access
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "mcp-server.log"))
    ]
)
logger = logging.getLogger("audacity-mcp")

def _send_command(command: str) -> str:
    """Internal helper to send a command to Audacity and read response."""
    if not validate_command(command):
        logger.warning(f"Blocked invalid or unsafe command: {command}")
        return "Error: Invalid or unsafe command. Command rejected by security policy."

    if not os.path.exists(WRITE_NAME) or not os.path.exists(READ_NAME):
        return "Error: Audacity pipes not found. Is Audacity running with mod-script-pipe enabled?"

    try:
        # On Linux/Mac, ensure pipes have restrictive permissions if we create them
        # (Audacity usually creates them, but we should verify if possible)
        
        with open(WRITE_NAME, 'w') as to_pipe:
            logger.info(f"Sending command: {command}")
            to_pipe.write(command + EOL)
            to_pipe.flush()

        with open(READ_NAME, 'r') as from_pipe:
            response = ""
            start_time = time.time()
            timeout = 5.0 # 5 seconds timeout for pipe reading
            
            while True:
                if time.time() - start_time > timeout:
                    logger.error("Timeout reading from Audacity pipe")
                    return "Error: Timeout communicating with Audacity."
                
                line = from_pipe.readline()
                if not line: # EOF
                    break
                if line == '\n' and len(response) > 0:
                    break
                response += line
            return response.strip()
    except Exception as e:
        logger.error(f"Error communicating with Audacity: {e}")
        return f"Error communicating with Audacity: {e}"

@mcp.tool()
@track_performance
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
@track_performance
def get_track_info() -> str:
    """Get information about all tracks in the current project."""
    return _send_command("GetInfo: Type=Tracks")

@mcp.tool()
@track_performance
def list_available_commands() -> str:
    """List all available scripting commands in Audacity."""
    return _send_command("Help: Command=Help")

@mcp.tool()
def health_check() -> dict:
    """Check the health of the MCP server and its connection to Audacity."""
    pipes_exist = os.path.exists(WRITE_NAME) and os.path.exists(READ_NAME)
    audacity_alive = False
    if pipes_exist:
        response = _send_command("Help: Command=Help")
        audacity_alive = "BatchCommand" in response # Simple check for a valid response

    return {
        "status": "ok" if audacity_alive else "degraded",
        "pipes_found": pipes_exist,
        "audacity_connected": audacity_alive,
        "platform": sys.platform,
        "log_directory": LOG_DIR
    }

@mcp.tool()
def get_metrics() -> dict:
    """Get performance metrics for the MCP server."""
    return metrics.get_summary()

if __name__ == "__main__":
    mcp.run()
