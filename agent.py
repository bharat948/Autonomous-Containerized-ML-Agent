import os
import sys
import json
import subprocess
import shlex

# List of forbidden command keywords/binaries for safety
FORBIDDEN_COMMANDS = [
    "sudo", "su", "chmod", "chown", "iptables", "docker", "docker-compose",
    "nc", "netcat", "ncat", "ssh", "scp", "sftp", "ftp", "telnet",
    "mkfs", "dd", "shutdown", "reboot", "poweroff", "init"
]

# Sensitive system files that must not be modified by agent tools
RESTRICTED_WRITE_FILES = [
    "agent.py", "setup_sandbox.sh", "teardown.sh", "verify_agent.sh", "verify_sandbox.sh", ".env"
]

def is_path_safe(file_path: str) -> (bool, str):
    """Normalizes path and checks whether it stays strictly inside /workspace."""
    clean_path = os.path.normpath(os.path.join("/workspace", file_path.lstrip("/")))
    if not clean_path.startswith("/workspace"):
        return False, "Error: Access denied. Path must remain inside /workspace directory."
    return True, clean_path

def is_command_safe(command: str) -> (bool, str):
    """Validates command string against forbidden binaries and risky operations."""
    tokens = command.strip().split()
    if not tokens:
        return False, "Error: Empty command provided."
    
    # Check forbidden command binaries
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden in tokens or any(t.endswith("/" + forbidden) for t in tokens):
            return False, f"Error: Command rejected due to security policy. Token '{forbidden}' is forbidden."
            
    # Check for direct modifications to agent core driver files
    for restricted in RESTRICTED_WRITE_FILES:
        if restricted in command:
            # Block destructive redirects or modifications
            for op in [">", ">>", "rm", "mv", "cp"]:
                if op in tokens:
                    return False, f"Error: Modifying control script '{restricted}' is restricted."

    return True, ""

def read_workspace_file(file_path: str) -> str:
    """Reads the contents of a file relative to the /workspace directory."""
    print(f"[TOOL RUN] Calling read_workspace_file with path: '{file_path}'", flush=True)
    safe, clean_path_or_err = is_path_safe(file_path)
    if not safe:
        return clean_path_or_err
        
    try:
        if not os.path.exists(clean_path_or_err):
            return f"Error: File not found at path: {file_path}"
        with open(clean_path_or_err, "r", encoding="utf-8", errors="ignore") as f:
            # Read up to 1MB to prevent memory or context overload
            content = f.read(1024 * 1024)
            return content
    except Exception as e:
        return f"Error reading file: {e}"

def write_workspace_file(file_path: str, content: str) -> str:
    """Writes text content to a file inside the /workspace directory."""
    print(f"[TOOL RUN] Calling write_workspace_file with path: '{file_path}'", flush=True)
    safe, clean_path_or_err = is_path_safe(file_path)
    if not safe:
        return clean_path_or_err

    filename = os.path.basename(clean_path_or_err)
    if filename in RESTRICTED_WRITE_FILES:
        return f"Error: Modifying core system script '{filename}' is restricted."

    try:
        # Create parent directories if needed
        os.makedirs(os.path.dirname(clean_path_or_err), exist_ok=True)
        with open(clean_path_or_err, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {e}"

def run_command_in_sandbox(command: str) -> str:
    """Executes a shell command inside the /workspace directory within the sandbox container."""
    print(f"[TOOL RUN] Calling run_command_in_sandbox with command: '{command}'", flush=True)
    safe, err_msg = is_command_safe(command)
    if not safe:
        return err_msg

    try:
        res = subprocess.run(
            command,
            shell=True,
            cwd="/workspace",
            capture_output=True,
            text=True,
            timeout=120
        )
        stdout = res.stdout.strip()
        stderr = res.stderr.strip()
        
        output_str = ""
        if stdout:
            output_str += f"STDOUT:\n{stdout}\n"
        if stderr:
            output_str += f"STDERR:\n{stderr}\n"
        if not output_str:
            output_str = "(Command produced no output)"
            
        output_str += f"\n[Exit Code: {res.returncode}]"
        return output_str
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 120 seconds."
    except Exception as e:
        return f"Error executing command: {e}"

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
        user_prompt = "Read the goal from goal.txt and execute the task steps to build, evaluate, and save the ML model."

    # Load system prompt from mounted directory
    prompt_path = "/workspace/system_prompt.txt"
    default_prompt = "You are a helpful assistant running inside an isolated Docker sandbox."
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
                            "description": "Path to the file inside /workspace (e.g., 'titanic.csv' or 'goal.txt')."
                        }
                    },
                    "required": ["file_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_workspace_file",
                "description": "Writes text content (code, plans, scripts, docs) to a file inside /workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Target relative file path inside /workspace (e.g., 'agent_plan.md', 'train.py')."
                        },
                        "content": {
                            "type": "string",
                            "description": "Text or code content to write."
                        }
                    },
                    "required": ["file_path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_command_in_sandbox",
                "description": "Executes a shell command (e.g., 'python train.py' or 'pip install scikit-learn') in /workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command string to run inside the container sandbox."
                        }
                    },
                    "required": ["command"]
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
    step_count = 0
    max_steps = 30  # Guard against infinite loop
    
    while step_count < max_steps:
        step_count += 1
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
        
        # Check if the model wants to call tools
        if message.tool_calls:
            messages.append(message)
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except Exception:
                    func_args = {}
                
                if func_name == "read_workspace_file":
                    tool_result = read_workspace_file(func_args.get("file_path", ""))
                elif func_name == "write_workspace_file":
                    tool_result = write_workspace_file(
                        func_args.get("file_path", ""),
                        func_args.get("content", "")
                    )
                elif func_name == "run_command_in_sandbox":
                    tool_result = run_command_in_sandbox(func_args.get("command", ""))
                else:
                    tool_result = f"Error: Tool '{func_name}' not recognized."
                    
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": str(tool_result)
                })
            continue
        else:
            # Final response
            print("\n=== LLM Response ===", flush=True)
            print(message.content, flush=True)
            print("====================\n", flush=True)
            print(f"Completed execution in {step_count} step(s).")
            break

if __name__ == "__main__":
    main()
