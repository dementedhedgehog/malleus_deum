import os
import sys
from pathlib import Path
from mcp.server.mcpserver import MCPServer
from os.path import abspath, join, dirname

src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))
ai_dir = join(root_dir, "ai")

def printe(msg):
    """
    The AI server talks to this thing using stdio so we'll use
    stderr for our error messages.
    
    """
    print(msg, file=sys.stderr)

# Initialize the file server
mcp = MCPServer("MalleusDeumFilesystem")

# Define an allowed root directory for safety
ALLOWED_READ_DIR = Path(root_dir).resolve()
ALLOWED_WRITE_DIR = Path(ai_dir).resolve()


def _validate_read_path(path: str) -> Path:
    """Check the path stays within the allowed directory."""
    full_path = (ALLOWED_READ_DIR / path).resolve()
    if not full_path.is_relative_to(ALLOWED_READ_DIR):
        raise ValueError(
            f"Access denied: Path {full_path} "
            "is outside the allowed directory.")
    return full_path

def _validate_write_path(path: str) -> Path:
    """Check the requested write path stays within the allowed directory."""
    full_path = (ALLOWED_WRITE_DIR / path).resolve()
    if not full_path.is_relative_to(ALLOWED_READ_DIR):
        raise ValueError(
            f"Access denied: Path {full_path} "
            "is outside the allowed directory.")
    return full_path

@mcp.tool()
def read_file(file_path: str) -> str:
    """Read and return the contents of a text file."""
    safe_path = _validate_read_path(file_path)
    if not safe_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    return safe_path.read_text(encoding="utf-8")

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """Write text content to a file inside the allowed directory."""
    safe_path = _validate_write_path(file_path)
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_text(content, encoding="utf-8")
    return f"Successfully wrote to {file_path}"

@mcp.tool()
def list_directory(dir_path: str = ".") -> list[str]:
    """List files and directories in the given path."""
    safe_path = _validate_read_path(dir_path)
    if not safe_path.is_dir():
        raise NotADirectoryError(f"Directory not found: {dir_path} ->{safe_path}")
    return os.listdir(safe_path)


if __name__ == "__main__":
    mcp.run(transport="stdio")
