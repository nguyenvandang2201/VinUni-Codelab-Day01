"""Collect real temperature experiment evidence; requires the user's API key."""

import importlib.util
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY. Configure it in the project .env file.")
    spec = importlib.util.spec_from_file_location("lab_submission", ROOT / "solution/solution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=30.0, max_retries=0)
    prompt = "Hãy kể cho tôi một sự thật thú vị về Việt Nam."
    rows = []
    output = ROOT / "reports/temperature_results.json"
    output.parent.mkdir(exist_ok=True)
    for temperature in (0.0, 0.5, 1.0, 1.5):
        import time

        started = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=module.OPENAI_MODEL, messages=[{"role": "user", "content": prompt}],
                temperature=temperature, top_p=1.0, max_tokens=256,
            )
        except Exception as error:
            # Provider error messages can contain fragments of credentials.
            raise SystemExit(
                f"Request failed: {type(error).__name__} "
                f"(HTTP {getattr(error, 'status_code', 'unknown')}). "
                "Check the local API key, billing/quota and connection."
            ) from None
        rows.append({
            "temperature": temperature, "response": response.choices[0].message.content,
            "latency_seconds": time.perf_counter() - started,
            "usage": response.usage.model_dump() if response.usage else None,
        })
        output.write_text(json.dumps({
            "collected_at": datetime.now(timezone(timedelta(hours=7))).isoformat(),
            "model": module.OPENAI_MODEL, "prompt": prompt, "top_p": 1.0,
            "max_tokens": 256, "results": rows,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved temperature={temperature}")
    print(output)


if __name__ == "__main__":
    main()
