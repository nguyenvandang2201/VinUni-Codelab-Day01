"""Checks for streamed turns and parameter forwarding beyond the basic rubric."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load_submission(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


submission = load_submission("solution/solution.py", "lms_behavior_solution")


def chunk(text):
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text))])


def test_stream_keeps_three_complete_turns_and_flushes(capsys):
    client = MagicMock()
    client.chat.completions.create.side_effect = [
        iter([SimpleNamespace(choices=[]), chunk(None), chunk(f"answer{i}")])
        for i in range(1, 6)
    ]
    with patch("openai.OpenAI", return_value=client), patch(
        "builtins.input", side_effect=[f"question{i}" for i in range(1, 6)] + ["quit"]
    ), patch("builtins.print", wraps=print) as printer:
        submission.streaming_chatbot()

    calls = client.chat.completions.create.call_args_list
    assert len(calls) == 5
    assert calls[-1].kwargs["messages"] == [
        {"role": role, "content": text}
        for role, text in [
            ("user", "question2"), ("assistant", "answer2"),
            ("user", "question3"), ("assistant", "answer3"),
            ("user", "question4"), ("assistant", "answer4"),
            ("user", "question5"),
        ]
    ]
    assert len(calls[0].kwargs["messages"]) == 1
    assert all(call.kwargs["stream"] for call in calls)
    printer.assert_any_call("answer1", end="", flush=True)
    assert "answer5" in capsys.readouterr().out


def test_failed_partial_stream_is_not_saved_as_history():
    def failed_stream():
        yield chunk("partial")
        raise RuntimeError("stream interrupted")

    client = MagicMock()
    client.chat.completions.create.side_effect = [
        iter([chunk("complete")]), failed_stream(), iter([chunk("recovered")])
    ]
    with patch("openai.OpenAI", return_value=client), patch(
        "builtins.input", side_effect=["first", "failed", "next", "quit"]
    ):
        submission.streaming_chatbot()
    assert client.chat.completions.create.call_args_list[-1].kwargs["messages"] == [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "complete"},
        {"role": "user", "content": "next"},
    ]


def test_empty_input_then_eof_does_not_need_credentials():
    with patch("openai.OpenAI") as constructor, patch(
        "builtins.input", side_effect=["  ", EOFError()]
    ):
        submission.streaming_chatbot()
    constructor.assert_not_called()


def test_mini_forwards_sampling_parameters():
    with patch.object(submission, "call_openai", return_value=("answer", 0.1)) as call:
        assert submission.call_openai_mini("prompt", 0.2, 0.8, 100) == ("answer", 0.1)
    call.assert_called_once_with(
        "prompt", model="gpt-4o-mini", temperature=0.2, top_p=0.8, max_tokens=100
    )


def test_batch_records_do_not_share_mutable_dictionaries():
    with patch.object(submission, "compare_models", return_value={"gpt4o_response": "answer"}):
        result = submission.batch_compare(["one", "two"])
    assert result[0]["prompt"] == "one"
    assert result[1]["prompt"] == "two"
    assert result[0] is not result[1]


def test_retry_schedule_and_final_exception():
    with patch.object(submission.time, "sleep") as sleep:
        with pytest.raises(RuntimeError, match="permanent"):
            submission.retry_with_backoff(
                MagicMock(side_effect=RuntimeError("permanent")), 3, 0.1
            )
    assert [call.args[0] for call in sleep.call_args_list] == [0.1, 0.2, 0.4]


@pytest.mark.parametrize("path", ["starter-code/template.py", "solution-code/solution.py"])
def test_gemini_accepts_google_api_key_alias(path, monkeypatch):
    module = load_submission(path, "alias_" + path.split("/")[0].replace("-", "_"))
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key-not-a-real-credential")
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(
        text="answer", usage_metadata=SimpleNamespace(prompt_token_count=1, candidates_token_count=2)
    )
    with patch("google.genai.Client", return_value=client) as constructor:
        answer, _, usage = module.call_gemini("hello")
    constructor.assert_called_once_with(api_key="test-key-not-a-real-credential")
    assert answer == "answer"
    assert usage == {"input_tokens": 1, "output_tokens": 2}
