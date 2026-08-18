import os
import sys
import json
import time
import uuid
import datetime
import subprocess

# Forbidden command binaries for security
FORBIDDEN_COMMANDS = [
    "sudo", "su", "chmod", "chown", "iptables", "docker", "docker-compose",
    "nc", "netcat", "ncat", "ssh", "scp", "sftp", "ftp", "telnet",
    "mkfs", "dd", "shutdown", "reboot", "poweroff", "init"
]

# Sensitive control files that must not be modified by agent tools
RESTRICTED_WRITE_FILES = [
    "agent.py", "setup_sandbox.sh", "teardown.sh", "verify_agent.sh", "verify_sandbox.sh", "run_agent.sh", ".env"
]

# Model Pricing per 1M tokens USD
MODEL_PRICING = {
    "gpt-4o-mini": {"prompt": 0.15 / 1_000_000, "completion": 0.60 / 1_000_000},
    "gemini-1.5-flash": {"prompt": 0.075 / 1_000_000, "completion": 0.30 / 1_000_000},
    "default": {"prompt": 0.15 / 1_000_000, "completion": 0.60 / 1_000_000}
}

def calculate_step_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculates USD cost for a given token usage."""
    pricing = MODEL_PRICING.get(model_name.lower(), MODEL_PRICING["default"])
    return (prompt_tokens * pricing["prompt"]) + (completion_tokens * pricing["completion"])

def is_path_safe(file_path: str) -> tuple[bool, str]:
    """Normalizes path and checks whether it stays strictly inside /workspace."""
    clean_path = os.path.normpath(os.path.join("/workspace", file_path.lstrip("/")))
    if not clean_path.startswith("/workspace"):
        return False, "Error: Access denied. Path must remain inside /workspace directory."
    return True, clean_path

def is_command_safe(command: str) -> tuple[bool, str]:
    """Validates command string against forbidden binaries and risky operations."""
    tokens = command.strip().split()
    if not tokens:
        return False, "Error: Empty command provided."
    
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden in tokens or any(t.endswith("/" + forbidden) for t in tokens):
            return False, f"Error: Command rejected due to security policy. Token '{forbidden}' is forbidden."
            
    for restricted in RESTRICTED_WRITE_FILES:
        if restricted in command:
            for op in [">", ">>", "rm", "mv", "cp"]:
                if op in tokens:
                    return False, f"Error: Modifying control script '{restricted}' is restricted."

    return True, ""

def trim_tool_output(content: str, max_chars: int = 10000) -> str:
    """Helper to trim massive tool output before appending to LLM memory."""
    if len(content) <= max_chars:
        return content
    half = max_chars // 2
    truncated_msg = f"\n\n... [TRUNCATED {len(content) - max_chars} CHARACTERS FOR CONTEXT CONSERVATION. Original length: {len(content)}] ...\n\n"
    return content[:half] + truncated_msg + content[-half:]

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
        os.makedirs(os.path.dirname(clean_path_or_err), exist_ok=True)
        with open(clean_path_or_err, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {e}"

def run_command_in_sandbox(command: str) -> str:
    """Executes a shell command inside /workspace directory within the sandbox container."""
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

def save_trace(trace_data: dict):
    """Saves structured JSON trace to /workspace/agent_trace.json."""
    try:
        trace_path = "/workspace/agent_trace.json"
        with open(trace_path, "w", encoding="utf-8") as f:
            json.dump(trace_data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not write trace log: {e}", file=sys.stderr, flush=True)

def main():
    session_id = str(uuid.uuid4())
    start_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Check env variables
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not openai_key and not gemini_key:
        print("Error: Neither OPENAI_API_KEY nor GEMINI_API_KEY was found in environment variables.", file=sys.stderr)
        sys.exit(1)
        
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: The 'openai' library is not installed inside the container environment.", file=sys.stderr)
        sys.exit(1)
        
    # Pick User Prompt from args or use default
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = "Read the goal from goal.txt and execute the task steps to build, evaluate, and save the ML model."

    # Load system prompt from /app/system_prompt.txt (or fallback to /workspace/system_prompt.txt)
    prompt_paths = ["/app/system_prompt.txt", "/workspace/system_prompt.txt"]
    system_prompt = "You are a helpful assistant running inside an isolated Docker sandbox."
    
    for p_path in prompt_paths:
        if os.path.exists(p_path):
            try:
                with open(p_path, "r") as f:
                    system_prompt = f.read().strip()
                print(f"Loaded system prompt from {p_path}", flush=True)
                break
            except Exception as e:
                print(f"Warning: Could not read system prompt file at {p_path}: {e}", file=sys.stderr, flush=True)

    # Pick client model
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
                "description": "Reads the text contents of a file inside /workspace.",
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
                "description": "Executes a shell command (e.g., 'python train.py') in /workspace.",
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
    
    trace_data = {
        "session_id": session_id,
        "start_time": start_time_iso,
        "end_time": None,
        "model": model,
        "user_prompt": user_prompt,
        "total_steps": 0,
        "total_tokens": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        },
        "total_cost_usd": 0.0,
        "steps": []
    }

    print(f"Prompt: \"{user_prompt}\"", flush=True)
    print(f"Calling LLM model '{model}' with tool support...", flush=True)
    
    step_count = 0
    max_steps = 30
    
    while step_count < max_steps:
        step_count += 1
        step_start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Reinforce system prompt with goal and plan state if they exist
        goal_content = ""
        if os.path.exists("/workspace/goal.txt"):
            try:
                with open("/workspace/goal.txt", "r", encoding="utf-8") as f:
                    goal_content = f.read().strip()
            except Exception:
                pass

        plan_content = ""
        if os.path.exists("/workspace/agent_plan.md"):
            try:
                with open("/workspace/agent_plan.md", "r", encoding="utf-8") as f:
                    plan_content = f.read().strip()
            except Exception:
                pass

        reinforced_prompt = system_prompt
        if goal_content or plan_content:
            reinforced_prompt += "\n\n## CURRENT STATE & TARGET REINFORCEMENT"
            if goal_content:
                reinforced_prompt += f"\n### TARGET OBJECTIVE (from goal.txt):\n{goal_content}"
            if plan_content:
                reinforced_prompt += f"\n### CURRENT AGENT PLAN STATE (from agent_plan.md):\n{plan_content}"
        
        messages[0]["content"] = reinforced_prompt

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"Error calling LLM: {e}", file=sys.stderr, flush=True)
            trace_data["end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            save_trace(trace_data)
            sys.exit(1)
            
        message = response.choices[0].message
        
        # Token extraction
        usage = getattr(response, "usage", None)
        p_tokens = usage.prompt_tokens if usage else 0
        c_tokens = usage.completion_tokens if usage else 0
        t_tokens = usage.total_tokens if usage else (p_tokens + c_tokens)
        
        step_cost = calculate_step_cost(model, p_tokens, c_tokens)
        
        # Update metrics accumulator
        trace_data["total_tokens"]["prompt_tokens"] += p_tokens
        trace_data["total_tokens"]["completion_tokens"] += c_tokens
        trace_data["total_tokens"]["total_tokens"] += t_tokens
        trace_data["total_cost_usd"] += step_cost
        trace_data["total_steps"] = step_count
        
        step_trace = {
            "step_number": step_count,
            "timestamp": step_start_time,
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "total_tokens": t_tokens,
            "step_cost_usd": round(step_cost, 6),
            "tool_calls": [],
            "tool_results": [],
            "llm_text_response": message.content if message.content else None
        }
        
        if message.tool_calls:
            messages.append(message)
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except Exception:
                    func_args = {}
                
                step_trace["tool_calls"].append({
                    "id": tool_call.id,
                    "name": func_name,
                    "arguments": func_args
                })
                
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
                    
                step_trace["tool_results"].append({
                    "id": tool_call.id,
                    "name": func_name,
                    "result_preview": str(tool_result)[:300]
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": trim_tool_output(str(tool_result))
                })
                
            trace_data["steps"].append(step_trace)
            save_trace(trace_data)
            continue
        else:
            trace_data["steps"].append(step_trace)
            trace_data["end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            save_trace(trace_data)
            
            print("\n=== LLM Final Response ===", flush=True)
            print(message.content, flush=True)
            print("===========================\n", flush=True)
            
            print("=== Token & Cost Summary ===", flush=True)
            print(f"Model:             {model}", flush=True)
            print(f"Total Steps:       {step_count}", flush=True)
            print(f"Prompt Tokens:     {trace_data['total_tokens']['prompt_tokens']:,}", flush=True)
            print(f"Completion Tokens: {trace_data['total_tokens']['completion_tokens']:,}", flush=True)
            print(f"Total Tokens:      {trace_data['total_tokens']['total_tokens']:,}", flush=True)
            print(f"Estimated Cost:    ${trace_data['total_cost_usd']:.6f} USD", flush=True)
            print(f"Trace Log Saved:   /workspace/agent_trace.json", flush=True)
            print("===========================\n", flush=True)
            break

if __name__ == "__main__":
    main()
