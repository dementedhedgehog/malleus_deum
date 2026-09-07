"""

    Little experiment in using AI for local code review
    (a failed experiment I'd say because the local AI models I can run are
    not smart enough).

"""
import sys
import os
import code
import threading
import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define which model to use.
# Note: Choose a model that supports Tool Calling (e.g., qwen2.5, llama3.1)
MODEL_NAME = "qwen3:8b" 



# Define your configuration
#MODEL_NAME = "qwen2.5:7b"
current_dir = os.path.dirname(os.path.abspath(__file__))
server_script_path = os.path.join(current_dir, "ai_mcp_server.py")

# Shared variables that will be available inside your REPL environment
session_context = {}
loop = None

def printe(msg):
    """
    The AI server talks to this thing using stdio so we'll use
    stderr for our error messages.
    
    """
    print(msg, file=sys.stderr)


def chat(prompt: str):
    """
    Helper function to send a prompt to Ollama with access to your MCP server tools.
    Usage in REPL: chat("List the files in my directory")
    """
    if "session" not in session_context:
        print("! MCP Session is not initialized yet.")
        return

    # A simple synchronous wrapper over the asynchronous chat loop logic
    async def _async_chat():
        session = session_context["session"]
        ollama_tools = session_context["tools"]
        
        # In a REPL, you might want to track a running context history. 
        # For simplicity, we manage a session-wide history list.
        if "history" not in session_context:
            session_context["history"] = [{
                "role": "system",
                "content": "You are a local developer assistant with access to the local filesystem via tools."
            }]
        
        history = session_context["history"]
        history.append({"role": "user", "content": prompt})
        
        while True:
            # Call Ollama
            response = ollama.chat(model=MODEL_NAME, messages=history, tools=ollama_tools)
            assistant_message = response.get('message', {})
            history.append(assistant_message)
            
            # Execute tool if requested
            if assistant_message.get('tool_calls'):
                for tool_call in assistant_message['tool_calls']:
                    tool_name = tool_call['function']['name']
                    tool_args = tool_call['function']['arguments']
                    
                    print(f" Executing server tool: {tool_name}({tool_args})...")
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    #tool_output = result.content.text
                    try:
                        output = []
                        for x in result.content:
                            output.append(x.text)
                        tool_output = "\n".join(output)
                    except TypeError:
                        tool_output = str(result.content)

                    print(f" Result: {tool_output}")
                    
                    history.append({"role": "tool", "name": tool_name, "content": tool_output})
                continue
            else:
                print(f"\n Ollama: {assistant_message.get('content', '')}")
                break

    # Run the coroutine safely on the background event loop
    future = asyncio.run_coroutine_threadsafe(_async_chat(), loop)
    future.result() # Blocks REPL thread until processing finishes

async def start_mcp_bridge():
    """Manages the lifetime of the background MCP server connection."""
    global loop
    loop = asyncio.get_running_loop()
    
    server_params = StdioServerParameters(
        command=sys.executable,  
        args=[server_script_path]
    )
    
    print(" Starting background MCP Filesystem Server...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Map tools
            mcp_tools = await session.list_tools()
            ollama_tools = []
            for tool in mcp_tools.tools:
                ollama_tools.append({
                    'type': 'function',
                    'function': {
                        'name': tool.name,
                        'description': tool.description,
                        'parameters': tool.input_schema  
                    }
                })
                
            # Expose references to the REPL environment
            session_context["session"] = session
            session_context["tools"] = ollama_tools
            
            print(" MCP Connection established! REPL is ready.")
            
            # Keep this coroutine alive while the REPL shell runs in the main thread
            while session_context.get("running", True):
                await asyncio.sleep(0.5)

def run_async_loop_in_background():
    """Runs the asyncio event loop in a dedicated background thread."""
    asyncio.run(start_mcp_bridge())

def list_dir():
    print("frog")
    
if __name__ == "__main__":
    session_context["running"] = True
    
    # 1. Spin up the background thread to handle the asynchronous network connection
    bg_thread = threading.Thread(target=run_async_loop_in_background, daemon=True)
    bg_thread.start()
    
    # 2. Give the background connection a moment to handshake
    import time
    time.sleep(2) 
    
    # 3. Define the namespace/variables we want exposed directly inside our REPL
    repl_vars = {
        "chat": chat,
        "ollama": ollama,
        "context": session_context,
        "ls": list_dir,    
    }
    
    # 4. Launch the standard Python REPL environment
    banner = (
        "==========================================================\n"
        " Welcome to the Interactive MCP Python REPL Shell!\n"
        "==========================================================\n"
        "Available commands:\n"
        "  -> chat(\"your natural language request\")\n"
        "  -> context['history']  (View current conversation log)\n"
        "  -> context['tools']    (View raw tool definitions)\n"
        "=========================================================="
    )
    
    code.interact(banner=banner, local=repl_vars)
    
    # Clean up background loop when exiting REPL
    session_context["running"] = False    
