from __future__ import annotations

import time
import uuid
from typing import Any

from app.schemas.openai import ChatCompletionRequest


def request_to_llm_payload(request: ChatCompletionRequest) -> dict[str, Any]:
    if request.stream:
        msg = "stream=true não é suportado; envie stream=false."
        raise ValueError(msg)
    data = request.model_dump(exclude_none=True)
    data.pop("session_id", None)
    data.pop("channel", None)
    return data


def llm_response_to_openai(resp: dict[str, Any], *, model: str) -> dict[str, Any]:
    out_id = resp.get("id")
    if not isinstance(out_id, str) or not out_id.strip():
        out_id = f"chatcmpl-{uuid.uuid4().hex}"

    created = resp.get("created")
    if isinstance(created, (int, float)):
        created_i = int(created)
    else:
        created_i = int(time.time())

    out_model = resp.get("model")
    if not isinstance(out_model, str) or not out_model.strip():
        out_model = model

    choices_in = resp.get("choices")
    choices_out = _normalize_openai_choices(choices_in)
    usage_out = _normalize_openai_usage(resp.get("usage"))

    return {
        "id": out_id,
        "object": "chat.completion",
        "created": created_i,
        "model": out_model,
        "choices": choices_out,
        "usage": usage_out,
    }


def _normalize_openai_choices(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        return [
            {
                "index": 0,
                "message": {"role": "assistant", "content": ""},
                "finish_reason": "stop",
            }
        ]

    out: list[dict[str, Any]] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        idx = item.get("index")
        if not isinstance(idx, int):
            idx = i
        message = _normalize_assistant_message(item.get("message"), item)
        finish = item.get("finish_reason")
        if finish is None:
            finish = "stop"
        if not isinstance(finish, str):
            finish = str(finish)
        out.append({"index": idx, "message": message, "finish_reason": finish})
    return out or [
        {
            "index": 0,
            "message": {"role": "assistant", "content": ""},
            "finish_reason": "stop",
        }
    ]


def _normalize_assistant_message(
    message: Any,
    choice: dict[str, Any],
) -> dict[str, Any]:
    if isinstance(message, dict):
        role = message.get("role")
        if not isinstance(role, str) or not role:
            role = "assistant"
        content = message.get("content")
        if content is not None and not isinstance(content, (str, list, dict)):
            content = str(content)
        return {"role": role, "content": content}

    text = choice.get("text")
    if isinstance(text, str):
        return {"role": "assistant", "content": text}
    return {"role": "assistant", "content": ""}


def _normalize_openai_usage(raw: Any) -> dict[str, int]:
    if not isinstance(raw, dict):
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _i(key: str) -> int:
        v = raw.get(key)
        if isinstance(v, bool) or v is None:
            return 0
        if isinstance(v, (int, float)):
            return max(0, int(v))
        try:
            return max(0, int(v))
        except (TypeError, ValueError):
            return 0

    pt = _i("prompt_tokens")
    ct = _i("completion_tokens")
    tt = _i("total_tokens")
    if tt == 0:
        tt = pt + ct
    return {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": tt}
