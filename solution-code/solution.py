"""
Day 1 — LLM API Foundation
AICB-P1: AI Practical Competency Program, Phase 1

Instructions:
    1. Fill in every section marked with TODO.
    2. Do NOT change function signatures.
    3. Copy this file to solution/solution.py when done.
    4. Run: pytest tests/ -v
"""

import os
import sys
import time
from typing import Any, Callable

# Load API keys from a .env file in the project root (if python-dotenv is installed).
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Estimated costs per 1M INPUT & OUTPUT tokens (USD) as of March 2026
# Vietnamese text generally consumes ~1.5x - 2.0x more tokens than English due to Unicode/diacritics.
# ---------------------------------------------------------------------------
PRICING_1M_TOKENS = {
    "gpt-4o": {"input": 5.00, "output": 20.00},
    "gpt-4o-mini": {"input": 0.150, "output": 0.600},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.300},
    "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku": {"input": 0.80, "output": 4.00},
}

# Standard Model Identifiers
OPENAI_MODEL = "gpt-4o"
OPENAI_MINI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-2.5-flash"
ANTHROPIC_MODEL = "claude-3-5-haiku"

# Claude 3.5 models were retired by Anthropic in 2026 and "claude-3-5-haiku" was never
# a valid API model ID, so these names are mapped to their current replacements when calling.
ANTHROPIC_MODEL_ALIASES = {
    "claude-3-5-haiku": "claude-haiku-5-5",
    "claude-3-5-sonnet": "claude-sonnet-5-5",
}

# Chatbot settings
CHATBOT_MAX_TURNS = 3  # 1 turn = 1 user message + 1 model reply


def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return the USD cost of one call based on PRICING_1M_TOKENS."""
    rates = PRICING_1M_TOKENS[model]
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


def _ensure_utf8_output() -> None:
    """Print Vietnamese text safely on consoles that default to a non-UTF-8 encoding (e.g. Windows cp1252)."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass


def _gemini_config(model: str, temperature: float, top_p: float, max_tokens: int):
    """Build a GenerateContentConfig for Gemini."""
    from google.genai import types

    config_kwargs = {
        "temperature": temperature,
        "top_p": top_p,
        "max_output_tokens": max_tokens,
    }
    # Gemini 2.5 Flash "thinks" by default and thinking tokens count toward
    # max_output_tokens, which can leave an empty answer with small limits.
    # Flash models allow turning thinking off (budget 0).
    if "flash" in model:
        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
    return types.GenerateContentConfig(**config_kwargs)


# ---------------------------------------------------------------------------
# Task 1 — Call OpenAI (GPT-4o)
# ---------------------------------------------------------------------------
def call_openai(
    prompt: str,
    model: str = OPENAI_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float, dict]:
    """
    Call the OpenAI Chat Completions API and return the response text, latency,
    and token usage stats.

    Args:
        prompt:      The user message to send.
        model:       The OpenAI model to use (default: gpt-4o).
        temperature: Sampling temperature (0.0 – 2.0).
        top_p:       Nucleus sampling threshold.
        max_tokens:  Maximum number of tokens to generate.

    Returns:
        A tuple of:
            - response_text (str)
            - latency_seconds (float)
            - usage (dict with keys: 'input_tokens', 'output_tokens')

    Hint:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # response.usage contains input_tokens and output_tokens (prompt_tokens/completion_tokens)
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )
    latency = time.perf_counter() - start

    text = response.choices[0].message.content or ""
    usage = {
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
    }
    return text, latency, usage


# ---------------------------------------------------------------------------
# Task 2 — Call Google Gemini 2.5 (Standard Practical Model)
# ---------------------------------------------------------------------------
def call_gemini(
    prompt: str,
    model: str = GEMINI_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float, dict]:
    """
    Call the Google Gemini API (using Gemini 2.5 Flash as standard) and return
    the response text, latency, and token usage stats.

    Args:
        prompt:      The user message to send.
        model:       The Gemini model to use (default: gemini-2.5-flash).
        temperature: Sampling temperature.
        top_p:       Nucleus sampling threshold.
        max_tokens:  Maximum number of tokens to generate.

    Returns:
        A tuple of:
            - response_text (str)
            - latency_seconds (float)
            - usage (dict with keys: 'input_tokens', 'output_tokens')

    Hint:
        Option A (New Google GenAI SDK):
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            # Configure using types.GenerateContentConfig
            
        Option B (Legacy Google GenerativeAI SDK):
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model_inst = genai.GenerativeModel(model)
            # Configure using genai.types.GenerationConfig
            
        Ensure your usage dictionary extracts 'input_tokens' and 'output_tokens' 
        from the response metadata (e.g. response.usage_metadata).
    """
    from google import genai

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    config = _gemini_config(model, temperature, top_p, max_tokens)

    start = time.perf_counter()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config,
    )
    latency = time.perf_counter() - start

    text = response.text or ""
    metadata = response.usage_metadata
    usage = {
        "input_tokens": (metadata.prompt_token_count or 0) if metadata else 0,
        "output_tokens": (metadata.candidates_token_count or 0) if metadata else 0,
    }
    return text, latency, usage


# ---------------------------------------------------------------------------
# Task 3 — Call Anthropic Claude (Exploratory track)
# ---------------------------------------------------------------------------
def call_anthropic(
    prompt: str,
    model: str = ANTHROPIC_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float, dict]:
    """
    Call the Anthropic Claude API (using Claude 3.5 Haiku as default) and return
    the response text, latency, and token usage stats.

    Args:
        prompt:      The user message to send.
        model:       The Claude model to use (default: claude-3-5-haiku).
        temperature: Sampling temperature (0.0 - 1.0).
        top_p:       Nucleus sampling threshold.
        max_tokens:  Maximum output tokens.

    Returns:
        A tuple of:
            - response_text (str)
            - latency_seconds (float)
            - usage (dict with keys: 'input_tokens', 'output_tokens')

    Hint:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # response.usage contains input_tokens and output_tokens
    """
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    api_model = ANTHROPIC_MODEL_ALIASES.get(model, model)

    # Note: temperature and top_p are kept in the signature for consistency with the
    # other providers, but they are NOT sent: the current Claude API (version 2026-10-21,
    # anthropic SDK >= 2.0) rejects sampling parameters on every model.
    start = time.perf_counter()
    response = client.messages.create(
        model=api_model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    latency = time.perf_counter() - start

    # The response is a list of content blocks; keep only the text blocks.
    text = "".join(
        block_text
        for block_text in (getattr(block, "text", None) for block in response.content)
        if isinstance(block_text, str)
    )
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return text, latency, usage


# ---------------------------------------------------------------------------
# Task 4 — Compare Models (OpenAI GPT-4o vs OpenAI Mini vs Gemini 2.5 Flash)
# ---------------------------------------------------------------------------
def compare_models(prompt: str) -> dict:
    """
    Call OpenAI (gpt-4o), OpenAI Mini (gpt-4o-mini), and Gemini 2.5 Flash (gemini-2.5-flash)
    with the same prompt and return a structured comparison dictionary.

    Calculate the exact USD token cost for input + output using the prices in PRICING_1M_TOKENS.

    Args:
        prompt: The user message to send to all models.

    Returns:
        A dictionary containing:
            - "gpt4o": { "response": str, "latency": float, "cost": float, "input_tokens": int, "output_tokens": int }
            - "gpt4o_mini": { "response": str, "latency": float, "cost": float, "input_tokens": int, "output_tokens": int }
            - "gemini_flash": { "response": str, "latency": float, "cost": float, "input_tokens": int, "output_tokens": int }
    """
    runs = [
        ("gpt4o", OPENAI_MODEL, call_openai(prompt, model=OPENAI_MODEL)),
        ("gpt4o_mini", OPENAI_MINI_MODEL, call_openai(prompt, model=OPENAI_MINI_MODEL)),
        ("gemini_flash", GEMINI_MODEL, call_gemini(prompt, model=GEMINI_MODEL)),
    ]

    results = {}
    for key, model, (text, latency, usage) in runs:
        input_tokens = usage["input_tokens"]
        output_tokens = usage["output_tokens"]
        results[key] = {
            "response": text,
            "latency": latency,
            "cost": _calculate_cost(model, input_tokens, output_tokens),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
    return results


# ---------------------------------------------------------------------------
# Task 5 — Streaming chatbot with Gemini 2.5 (Focus Model)
# ---------------------------------------------------------------------------
def streaming_chatbot() -> None:
    """
    Run an interactive streaming chatbot in the terminal using Gemini 2.5.

    Behaviour:
        - Streams response tokens from Gemini 2.5 Flash as they arrive.
        - Maintains the last 3 turns of conversation history for context.
        - Typing 'quit' or 'exit' ends the session.

    Hints:
        - Maintain a history list of conversation turns.
        - Check how to stream responses using client.chats or model.generate_content(..., stream=True).
        - Keep history limited to the last 3 turns to optimize context window and costs.
    """
    from google import genai
    from google.genai import types

    _ensure_utf8_output()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    config = _gemini_config(GEMINI_MODEL, temperature=0.7, top_p=0.9, max_tokens=1024)
    history: list = []  # alternating user / model messages
    max_messages = CHATBOT_MAX_TURNS * 2

    print("Gemini chatbot ready. Type 'quit' or 'exit' to end the session.")
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        # Context = the last 3 turns + the new question.
        contents = history + [
            types.Content(role="user", parts=[types.Part(text=user_input)])
        ]

        print("Gemini: ", end="", flush=True)
        reply_parts = []
        try:
            for chunk in client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=contents,
                config=config,
            ):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    reply_parts.append(chunk.text)
        except Exception as e:
            # Keep the chat alive; the failed turn is not added to history.
            print(f"\n[Error] {e}")
            continue
        print()

        history = contents + [
            types.Content(role="model", parts=[types.Part(text="".join(reply_parts))])
        ]
        history = history[-max_messages:]


# ---------------------------------------------------------------------------
# Bonus Task A — Retry with exponential backoff
# ---------------------------------------------------------------------------
def retry_with_backoff(
    fn: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 0.1,
) -> Any:
    """
    Call fn(). If it raises an exception, retry up to max_retries times
    with exponential backoff (delay = base_delay * 2^attempt).

    Args:
        fn:          Zero-argument callable to execute.
        max_retries: Maximum number of retry attempts.
        base_delay:  Initial delay in seconds before the first retry.

    Returns:
        The return value of fn() on success.

    Raises:
        The last exception raised by fn() after all retries are exhausted.
    """
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception:
            if attempt == max_retries:
                raise  # out of retries: re-raise the last exception
            time.sleep(base_delay * (2 ** attempt))


# ---------------------------------------------------------------------------
# Bonus Task B — Batch compare
# ---------------------------------------------------------------------------
def batch_compare(prompts: list[str]) -> list[dict]:
    """
    Run compare_models on each prompt in the list.

    Args:
        prompts: List of prompt strings.

    Returns:
        List of dicts, each being the compare_models result with an extra
        key "prompt" containing the original prompt string.
    """
    results = []
    for prompt in prompts:
        result = compare_models(prompt)
        result["prompt"] = prompt
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# Bonus Task C — Format comparison table
# ---------------------------------------------------------------------------
def format_comparison_table(results: list[dict]) -> str:
    """
    Format a list of batch compare results as a readable Markdown table string.

    Args:
        results: List of dicts as returned by batch_compare.

    Returns:
        A beautiful Markdown table string with columns:
        | Prompt | Model | Response (truncated) | Latency | Tokens (In/Out) | Cost (USD) |
    """
    model_labels = {
        "gpt4o": "GPT-4o",
        "gpt4o_mini": "GPT-4o-Mini",
        "gemini_flash": "Gemini-Flash",
    }

    def _cell(value: Any, limit: int | None = None) -> str:
        # Keep each value on one line and escape "|" so the table does not break.
        text = " ".join(str(value).split()).replace("|", "\\|")
        if limit is not None and len(text) > limit:
            text = text[:limit].rstrip() + "..."
        return text

    lines = [
        "| Prompt | Model | Response (truncated) | Latency | Tokens (In/Out) | Cost (USD) |",
        "|---|---|---|---|---|---|",
    ]
    for result in results:
        prompt = result.get("prompt", "")
        for key, stats in result.items():
            if key == "prompt":
                continue
            lines.append(
                f"| {_cell(prompt, 50)} "
                f"| {model_labels.get(key, key)} "
                f"| {_cell(stats['response'], 50)} "
                f"| {stats['latency']:.2f}s "
                f"| {stats['input_tokens']}/{stats['output_tokens']} "
                f"| ${stats['cost']:.8f} |"
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point for manual testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _ensure_utf8_output()
    print("=== Model Comparison Test ===")
    test_prompt = "Hãy giải thích sự khác biệt giữa temperature và top_p bằng tiếng Việt ngắn gọn trong 2 câu."
    try:
        # Note: Requires valid API keys set in environment variables
        result = compare_models(test_prompt)
        for model_name, stats in result.items():
            print(f"\n[{model_name.upper()}]")
            print(f"Latency: {stats['latency']:.2f}s | Cost: ${stats['cost']:.6f}")
            print(f"Tokens: {stats['input_tokens']} in / {stats['output_tokens']} out")
            print(f"Response: {stats['response']}")
    except Exception as e:
        print(f"Skipping live API comparison test: {e}")
        print("Set your API keys to run manual tests.")

    print("\n=== Starting Gemini 2.5 Chatbot (type 'quit' to exit) ===")
    try:
        streaming_chatbot()
    except Exception as e:
        print(f"Chatbot failed to start: {e}")
