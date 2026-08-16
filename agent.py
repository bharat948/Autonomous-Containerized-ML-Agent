import os
import sys
import json

# Implement the actual tool function
def read_workspace_file(file_path: str) -> str:
    """Reads the contents of a file relative to the /workspace directory."""
    print(f"[TOOL RUN] Calling read_workspace_file with path: '{file_path}'", flush=True)
    # Basic path safety check: restrict directory traversal outside of /workspace
    clean_path = os.path.normpath(os.path.join("/workspace", file_path.lstrip("/")))
    if not clean_path.startswith("/workspace"):
        return "Error: Access denied. Paths must remain inside the /workspace directory."
        
    try:
        if not os.path.exists(clean_path):
            return f"Error: File not found at path: {file_path}"
        with open(clean_path, "r", encoding="utf-8", errors="ignore") as f:
            # Read first 1MB to prevent OOM / context window overflow on giant files
            content = f.read(1024 * 1024)
            return content
    except Exception as e:
        return f"Error reading file: {e}"

def main():
    # Check env variables
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not openai_key and not gemini_key:
        print("Error: Neither OPENAI_API_KEY nor GEMINI_API_KEY was found in environment variables.", file=sys.stderr)
        sys.exit(1)
        
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: The 'openai' library is not installed inside the container environment. Install it via pip first.", file=sys.stderr)
        sys.exit(1)
        
    # Pick User Prompt from args or use default
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = "Read the first 3 lines of titanic.csv using your tools, and summarize it in one sentence."

    # Load system prompt from mounted directory
    prompt_path = "/workspace/system_prompt.txt"
    default_prompt = "You are a helpful assistant running inside an isolated Docker sandbox. Answer in one short sentence confirming your execution environment."
    system_prompt = default_prompt
    
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read().strip()
            print(f"Loaded system prompt from {prompt_path}", flush=True)
        except Exception as e:
            print(f"Warning: Could not read system prompt file: {e}", file=sys.stderr, flush=True)
    else:
        print("System prompt file not found, using default inline prompt.", flush=True)

    # Pick the available client
    if openai_key:
        print("Initializing LLM client using OpenAI URL...", flush=True)
        client = OpenAI(api_key=openai_key)
        model = "gpt-4o-mini"
    else:
        print("Initializing LLM client using Gemini OpenAI-compatible URL...", flush=True)
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model = "gemini-1.5-flash"
        
    # Tool declarations
    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_workspace_file",
                "description": "Reads the text contents of a file inside the /workspace directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file inside /workspace (e.g., 'titanic.csv' or 'readme.md')."
                        }
                    },
                    "required": ["file_path"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    print(f"Prompt: \"{user_prompt}\"", flush=True)
    print(f"Calling LLM model '{model}' with tool support...", flush=True)
    
    # Execution Reasoning Loop
    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"Error calling LLM: {e}", file=sys.stderr, flush=True)
            sys.exit(1)
            
        message = response.choices[0].message
        
        # Check if the model wants to call a tool
        if message.tool_calls:
            # Append model's thought/response to conversation history
            messages.append(message)
            
            # Execute tool calls
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                if func_name == "read_workspace_file":
                    tool_result = read_workspace_file(func_args.get("file_path"))
                else:
                    tool_result = f"Error: Tool '{func_name}' not implemented."
                    
                # Append tool response block
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": str(tool_result)
                })
            # Continue looping to let model analyze tool output
            continue
        else:
            # No tool calls requested, print the final answer
            print("\n=== LLM Response ===", flush=True)
            print(message.content, flush=True)
            print("====================\n", flush=True)
            print("Connection verification passed successfully!")
            break

if __name__ == "__main__":
    main()
