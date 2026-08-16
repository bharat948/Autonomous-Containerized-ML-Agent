import os
import sys

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
        # Gemini handles OpenAI API compatibility
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model = "gemini-1.5-flash"
        
    print(f"Calling LLM model '{model}'...", flush=True)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Hello! Confirm you can read this message."}
            ],
            max_tokens=100
        )
        print("\n=== LLM Response ===", flush=True)
        print(response.choices[0].message.content, flush=True)
        print("====================\n", flush=True)
        print("Connection verification passed successfully!")
    except Exception as e:
        print(f"Error calling LLM: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
