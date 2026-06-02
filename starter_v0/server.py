from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
load_lab_env(ROOT)

from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools

SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"

system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(tool_declarations)

provider = make_provider("groq")

app = FastAPI(title="Research Agent Chat")

STATIC_DIR = ROOT / "static"


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = []


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/tools")
async def list_tools():
    return tool_declarations


@app.get("/api/config")
async def get_config():
    return {
        "model": getattr(provider, "default_model", "unknown"),
        "tools_count": len(tool_declarations),
    }


def execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return {"error": "unknown_tool"}
    try:
        return func(**args)
    except Exception as exc:
        return {"error": type(exc).__name__, "message": str(exc)}


def build_tool_messages(
    messages: list[dict[str, str]],
    calls: list[ToolCall],
) -> list[dict[str, str]]:
    msgs = list(messages)
    for call in calls:
        result = execute_tool(call.name, call.args)
        msgs.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": call.name, "type": "function", "function": {"name": call.name, "arguments": json.dumps(call.args)}}],
        })
        msgs.append({
            "role": "tool",
            "tool_call_id": call.name,
            "content": json.dumps(result, ensure_ascii=False),
        })
    return msgs


async def stream_responses(messages: list[dict[str, str]]):
    loop = asyncio.get_event_loop()

    def call_llm(
        msgs: list[dict[str, str]],
        tools: list | None = None,
        tool_choice: Any | None = None,
    ):
        return provider.complete(msgs, tools if tools else openai_tools, temperature=0.0, tool_choice=tool_choice)

    try:
        response = await loop.run_in_executor(None, call_llm, messages, openai_tools, None)

        if response.text:
            yield {"type": "text", "content": response.text}

        if response.tool_calls:
            for call in response.tool_calls:
                yield {"type": "tool_call", "content": {"name": call.name, "args": call.args}}

            for call in response.tool_calls:
                result = await loop.run_in_executor(None, execute_tool, call.name, call.args)
                yield {"type": "tool_result", "content": {"tool": call.name, "result": result}}

            tool_msgs = build_tool_messages(messages, response.tool_calls)
            final = await loop.run_in_executor(None, call_llm, tool_msgs, openai_tools, None)

            if final.text:
                yield {"type": "text", "content": final.text}

            if final.tool_calls:
                for call in final.tool_calls:
                    yield {"type": "tool_call", "content": {"name": call.name, "args": call.args}}
                for call in final.tool_calls:
                    result = await loop.run_in_executor(None, execute_tool, call.name, call.args)
                    yield {"type": "tool_result", "content": {"tool": call.name, "result": result}}

    except Exception as exc:
        yield {"type": "error", "content": f"{type(exc).__name__}: {str(exc)}"}


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    messages = [{"role": "system", "content": system_prompt}]
    for h in req.history:
        messages.append(h)
    messages.append({"role": "user", "content": req.message})

    async def event_stream():
        async for event in stream_responses(messages):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
