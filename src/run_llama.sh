#!/usr/bin/env bash
set -x
#
# Runs llama locally with read access to most of the malleus deum dirs.
# (I know this is a bit of an eccentric way to do this).
#


#
# ONE TIME
# 
# 1. install llama
# 2. install the mcphost
#       go install github.com/mark3labs/mcphost@latest
# 3. Create a restricted system user for your AI tasks
#       sudo useradd -m -s /bin/bash ai_runner
# 
#


#
# Setup the MCP filesystem gateway.
#

# Give the AI user read-only access to your target folder
# Get the directory of the script, resolving symbolic links
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd -P)
# Get the parent directory of that script directory
PROJ_ROOT_DIR=$(dirname "$SCRIPT_DIR")
# AI sandbox
AI_DIR="$PROJ_ROOT_DIR/ai"
# MCPHOST executable
MCPHOST=/home/blaize/go/bin/mcphost

# Make sure everything is read only and kept up to date.
echo "Making $PROJ_ROOT_DIR read only"
sudo chmod -R o-wx+r "$PROJ_ROOT_DIR"

# Give the AI somewhere to write to
echo "Making $AI_DIR read/write only"
mkdir -p "$AI_DIR"
sudo chmod -R o+rwx "$AI_DIR"

# Give the AI permissions to run mcphost
echo "Making $MCPHOST executable"
sudo chmod -R o+rx "$MCPHOST"

# Let the ai_runner have read/execute access
sudo setfacl -R -m u:ai_runner:rx $MCPHOST
sudo chmod a+rx $PROJ_ROOT_DIR/..
sudo chmod a+rx $PROJ_ROOT_DIR
sudo chmod a+rx $SCRIPT_DIR

# Launch your MCP host switch-usered into the AI user
sudo -u ai_runner \
     $MCPHOST -m ollama:qwen3:8b \
     --config $SCRIPT_DIR/mcp-servers.json \
     --system-prompt "You are a development assistant. You have two separate filesystem servers. 
  1. For LISTING directories or READING files inside '/home/blaize/proj/malleus_deum', you MUST use 'malleus-reader__' tools. Never try to create files or directories with this server.
  2. For WRITING, EDITING, or CREATING directories, you MUST use 'malleus-writer__' tools, and you are strictly limited to the subfolder path: '/home/blaize/proj/malleus_deum/ai/'. Never call 'malleus-writer__create_directory' on the parent project folder."
