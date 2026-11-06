"""Day 01 LMS assignment: OpenAI calls, comparison, streaming and bonus tasks.

This submission follows the two-value return signatures in the LMS assignment.
The separate starter-code/ lab keeps its three-provider API and token usage.
"""

import os
import time
from pathlib import Path
from typing import Any, Callable

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

OPENAI_MODEL = "gpt-4o"
OPENAI_MINI_MODEL = "gpt-4o-mini"
CHATBOT_MAX_TURNS = 3

# Fixed classroom rates from the assignment, not current billing prices.
COST_PER_1K_OUTPUT_TOKENS = {"gpt-4o": 0.010, "gpt-4o-mini": 0.0006}


def call_openai(
    prompt: str,
    model: str = OPENAI_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float]:
    """Return the Chat Completions answer and elapsed seconds."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    started = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or "", time.perf_counter() - started


def call_openai_mini(
    prompt: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float]:
    """Use the same request implementation with GPT-4o-mini."""
    return call_openai(
        prompt, model=OPENAI_MINI_MODEL, temperature=temperature,
        top_p=top_p, max_tokens=max_tokens,
    )


def compare_models(prompt: str) -> dict:
    """Compare both models using the output-only approximation in the rubric."""
    answer, latency = call_openai(prompt)
    mini_answer, mini_latency = call_openai_mini(prompt)
    return {
        "gpt4o_response": answer,
        "mini_response": mini_answer,
        "gpt4o_latency": latency,
        "mini_latency": mini_latency,
        "gpt4o_cost_estimate": (
            len(answer.split()) / 0.75 / 1000
            * COST_PER_1K_OUTPUT_TOKENS[OPENAI_MODEL]
        ),
    }


def streaming_chatbot() -> None:
    """Stream answers with the previous three complete user/assistant turns."""
    from openai import OpenAI

    client = None
    history: list[dict[str, str]] = []
    print("OpenAI chatbot. Type 'quit' or 'exit' to finish.")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return
        if question.lower() in {"quit", "exit"}:
            print("Goodbye!")
            return
        if not question:
            continue

        # Build a fresh list: SDK calls and mocks must not see later mutations.
        messages = history + [{"role": "user", "content": question}]
        parts: list[str] = []
        print("Assistant: ", end="", flush=True)
        try:
            if client is None:
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            stream = client.chat.completions.create(
                model=OPENAI_MODEL, messages=messages, stream=True,
                max_tokens=1024,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                text = chunk.choices[0].delta.content
                if text:
                    print(text, end="", flush=True)
                    parts.append(text)
        except Exception as error:
            # Preserve only complete turns, including after a partial stream fails.
            print(f"\n[Error] {type(error).__name__}; check credentials, quota or connection.")
            continue
        print()
        history = (
            messages + [{"role": "assistant", "content": "".join(parts)}]
        )[-CHATBOT_MAX_TURNS * 2:]


def retry_with_backoff(
    fn: Callable, max_retries: int = 3, base_delay: float = 0.1,
) -> Any:
    """Try once, then retry up to max_retries times with doubling delays."""
    if max_retries < 0 or base_delay < 0:
        raise ValueError("max_retries and base_delay must be non-negative")
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(base_delay * 2 ** attempt)


def batch_compare(prompts: list[str]) -> list[dict]:
    """Return an independent comparison record for each prompt."""
    return [dict(compare_models(prompt), prompt=prompt) for prompt in prompts]


def format_comparison_table(results: list[dict]) -> str:
    """Render a compact Markdown table, escaping newlines and separators."""
    def cell(value: Any) -> str:
        text = " ".join(str(value).split())
        if len(text) > 40:
            text = text[:40] + "..."
        return text.replace("|", "\\|")

    lines = [
        "| Prompt | GPT-4o Response | Mini Response | GPT-4o Latency | Mini Latency |",
        "|---|---|---|---|---|",
    ]
    for row in results:
        lines.append(
            f"| {cell(row['prompt'])} | {cell(row['gpt4o_response'])} "
            f"| {cell(row['mini_response'])} | {row['gpt4o_latency']:.3f}s "
            f"| {row['mini_latency']:.3f}s |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in your environment or the project .env file.")
        raise SystemExit(1)
    print(format_comparison_table(batch_compare([
        "Explain the difference between temperature and top_p in one sentence."
    ])))
    streaming_chatbot()
