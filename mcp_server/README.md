# Audacity MCP Server

This server provides a Model Context Protocol (MCP) interface to Audacity 4. It allows AI agents to interact with Audacity by sending scripting commands via named pipes.

## Prerequisites

1. **Audacity 4**: Ensure you have Audacity 4 installed and running.
2. **mod-script-pipe**: This module must be enabled in Audacity.
   - Go to `Edit` -> `Preferences` -> `Modules`.
   - Set `mod-script-pipe` to `Enabled`.
   - Restart Audacity.
3. **Python 3.10+**: Required for the MCP server.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

You can run the server directly using Python:

```bash
python mcp_audacity.py
```

The server uses `stdio` as the transport mechanism.

## Tools Provided

- `audacity_command(command)`: Send a raw command to Audacity.
- `get_track_info()`: Get information about tracks in the project.
- `list_available_commands()`: List all supported commands in Audacity.

## Configuration for Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "audacity": {
      "command": "python3",
      "args": ["/path/to/my-audacity/mcp_server/mcp_audacity.py"]
    }
  }
}
```

## Security Considerations

- **Local Only**: The named pipes are restricted to the local user.
- **Command Injection**: Arguments are passed as strings to Audacity. Users should be aware that Audacity commands can perform file operations.
