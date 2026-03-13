"""
LLM-driven agent that uses tool/function calling so the model decides which tools
to call and in what order (assignment: avoid "hard-coded scripts without LLM decision-making").
"""

from __future__ import annotations

import json
import os
from typing import Callable, Optional

# Tool definitions for OpenAI function calling
FILTERING_TOOL = {
    "type": "function",
    "function": {
        "name": "filtering_tool",
        "description": "Filter the job dataset by the candidate's profile. Apply rules: location preference, years of experience limit, skills overlap, and company exclusion (e.g. FAANG). You must call this first before ranking or tailoring.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

RANKING_TOOL = {
    "type": "function",
    "function": {
        "name": "ranking_tool",
        "description": "Rank the filtered jobs by how well they match the candidate (skill match, title, location, experience). Call this after filtering_tool. Returns a ranked list with scores.",
        "parameters": {
            "type": "object",
            "properties": {
                "top_n": {
                    "type": "integer",
                    "description": "Number of top jobs to return (default 10)",
                }
            },
            "required": [],
        },
    },
}

RESUME_TAILORING_TOOL = {
    "type": "function",
    "function": {
        "name": "resume_tailoring_tool",
        "description": "Generate a tailored resume for one of the ranked jobs: rewrite the professional summary and exactly two experience bullet points. Call this after ranking_tool. Use job_rank=1 for the best (top-ranked) job.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_rank": {
                    "type": "integer",
                    "description": "1-based rank of the job (1 = best match)",
                }
            },
            "required": ["job_rank"],
        },
    },
}

OPENAI_TOOLS = [FILTERING_TOOL, RANKING_TOOL, RESUME_TAILORING_TOOL]

# Anthropic tool definitions (name, description, input_schema)
ANTHROPIC_TOOLS = [
    {
        "name": "filtering_tool",
        "description": FILTERING_TOOL["function"]["description"],
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "ranking_tool",
        "description": RANKING_TOOL["function"]["description"],
        "input_schema": {
            "type": "object",
            "properties": {"top_n": {"type": "integer", "description": "Number of top jobs to return (default 10)"}},
            "required": [],
        },
    },
    {
        "name": "resume_tailoring_tool",
        "description": RESUME_TAILORING_TOOL["function"]["description"],
        "input_schema": {
            "type": "object",
            "properties": {"job_rank": {"type": "integer", "description": "1-based rank (1 = best job)"}},
            "required": ["job_rank"],
        },
    },
]


def _detect_provider() -> str:
    provider = (os.environ.get("LLM_PROVIDER") or "").lower()
    if provider:
        return provider
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "ollama"


def run_llm_tool_agent(
    profile_summary: str,
    job_count: int,
    execute_tool: Callable[[str, dict], str],
    provider: Optional[str] = None,
    max_steps: int = 10,
) -> tuple[str, bool]:
    """
    Run an LLM-driven agent that decides which tools to call and in what order.

    Args:
        profile_summary: Short text describing the candidate (for the prompt).
        job_count: Number of jobs in the dataset.
        execute_tool: Callback (tool_name, arguments_dict) -> result_string.
        provider: "openai", "anthropic", or "ollama". Auto-detected if None.
        max_steps: Maximum tool-call rounds.

    Returns:
        (reasoning_trace, success). reasoning_trace is the full conversation/trace;
        success is True if the LLM completed the workflow (called tailor).
    """
    provider = provider or _detect_provider()
    system_msg = (
        "You are an AI job search agent. You have access to three tools that you must use in order:\n"
        "1. filtering_tool - Filter jobs by the candidate's profile (location, experience, skills, company exclusion). Call this first.\n"
        "2. ranking_tool - Rank the filtered jobs by match score. Call this after filtering.\n"
        "3. resume_tailoring_tool - Tailor the resume for the top job (summary + 2 bullets). Call this last with job_rank=1.\n"
        "You must decide when to call each tool. Call exactly one tool per turn. After each tool result, decide the next tool or finish."
    )
    user_msg = (
        f"Candidate profile:\n{profile_summary}\n\n"
        f"There are {job_count} jobs in the dataset. "
        "Decide which tool to call first and call it. Then use the result to decide the next step until you have completed filtering, ranking, and resume tailoring for the top job."
    )
    messages: list[dict] = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]
    reasoning_parts: list[str] = []
    success = False

    if provider == "ollama":
        # Ollama: no tool calling support in this agent
        reasoning_parts.append(_run_single_reasoning(system_msg, user_msg, provider))
        return "\n".join(reasoning_parts), False

    anthropic_messages: list[dict] = [{"role": "user", "content": user_msg}] if provider == "anthropic" else []

    for step in range(max_steps):
        if provider == "openai":
            out = _openai_tool_step(messages, reasoning_parts, execute_tool)
        elif provider == "anthropic":
            out = _anthropic_tool_step(system_msg, anthropic_messages, reasoning_parts, execute_tool)
        else:
            break
        if out is None:
            break
        if out == "done":
            success = True
            break
        # out == "continue" -> loop again

    return "\n\n".join(reasoning_parts), success


def _openai_tool_step(
    messages: list[dict],
    reasoning_parts: list[str],
    execute_tool: Callable[[str, dict], str],
) -> Optional[str]:
    """One OpenAI turn. Returns 'continue', 'done', or None (error/stop)."""
    try:
        from openai import OpenAI
    except ImportError:
        return None
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        messages=messages,
        tools=OPENAI_TOOLS,
        tool_choice="auto",
        temperature=0.2,
        max_tokens=1024,
    )
    msg = resp.choices[0].message
    if msg.content:
        reasoning_parts.append(f"Agent: {msg.content}")
    tool_calls = getattr(msg, "tool_calls", None) or []
    if not tool_calls:
        return "done"
    messages.append(
        {"role": "assistant", "content": msg.content or "", "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in tool_calls]}
    )
    for tc in tool_calls:
        name = tc.function.name
        try:
            args = json.loads(tc.function.arguments) if tc.function.arguments else {}
        except json.JSONDecodeError:
            args = {}
        result = execute_tool(name, args)
        reasoning_parts.append(f"Tool {name}({args}) -> {result}")
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    return "continue"


def _anthropic_tool_step(
    system_msg: str,
    anthropic_messages: list[dict],
    reasoning_parts: list[str],
    execute_tool: Callable[[str, dict], str],
) -> Optional[str]:
    """One Anthropic (Claude) turn with tool use. Mutates anthropic_messages for the next call."""
    try:
        import anthropic
    except ImportError:
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=os.environ.get("ANTHROPIC_CHAT_MODEL", "claude-3-5-sonnet-20240620"),
        max_tokens=1024,
        system=system_msg,
        messages=anthropic_messages,
        tools=ANTHROPIC_TOOLS,
    )
    text_parts = []
    tool_uses = []
    for block in getattr(resp, "content", []):
        btype = getattr(block, "type", "")
        if btype == "text":
            text_parts.append(getattr(block, "text", ""))
        elif btype == "tool_use":
            tool_uses.append(block)
    if text_parts:
        reasoning_parts.append("Agent: " + "\n".join(text_parts))
    if not tool_uses:
        return "done"
    tool_results = []
    for tu in tool_uses:
        name = getattr(tu, "name", "")
        inp = getattr(tu, "input", None) or {}
        tid = getattr(tu, "id", "")
        result = execute_tool(name, inp)
        reasoning_parts.append(f"Tool {name}({inp}) -> {result}")
        tool_results.append({"type": "tool_result", "tool_use_id": tid, "content": result})
    anthropic_messages.append({"role": "assistant", "content": resp.content})
    anthropic_messages.append({"role": "user", "content": tool_results})
    return "continue"


def _run_single_reasoning(system_msg: str, user_msg: str, provider: str) -> str:
    """Single reasoning step when tool calling is not used (Ollama or Anthropic)."""
    if provider == "anthropic":
        try:
            import anthropic
        except ImportError:
            return "Anthropic not available."
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "ANTHROPIC_API_KEY not set."
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=os.environ.get("ANTHROPIC_CHAT_MODEL", "claude-3-5-sonnet-20240620"),
            max_tokens=512,
            system=system_msg,
            messages=[{"role": "user", "content": user_msg}],
        )
        parts = [b.text for b in getattr(resp, "content", []) if getattr(b, "type", "") == "text"]
        return "\n".join(parts) if parts else "No response."
    # Ollama
    try:
        import requests
    except ImportError:
        return "Ollama not available."
    payload = {
        "model": os.environ.get("OLLAMA_MODEL", "llama3"),
        "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
        "stream": False,
    }
    r = requests.post("http://localhost:11434/api/chat", data=json.dumps(payload), timeout=60)
    if not r.ok:
        return "Ollama unavailable."
    text = (r.json().get("message") or {}).get("content", "")
    return text or "No response."
