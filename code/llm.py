"""
ProofLayer - Multi-LLM Orchestration Layer
Supports: OpenAI, Anthropic, Ollama (local/free)
Routing: cheap models for extraction, strong models for reasoning
"""

import os
import time
import httpx
from typing import Optional

# ─── Cost tracking (per 1K tokens, approximate) ───────────────────────────────
MODEL_COSTS = {
    "gpt-4o-mini":          {"input": 0.00015,  "output": 0.0006},
    "gpt-4o":               {"input": 0.005,    "output": 0.015},
    "claude-haiku-4-5-20251001":  {"input": 0.00025, "output": 0.00125},
    "claude-sonnet-4-6":    {"input": 0.003,    "output": 0.015},
    "ollama/llama3":        {"input": 0.0,      "output": 0.0},
    "ollama/mistral":       {"input": 0.0,      "output": 0.0},
}

# Global usage log for cost dashboard
usage_log: list[dict] = []


# ─── Smart Routing ─────────────────────────────────────────────────────────────
def route_task(task_type: str, content_length: int = 0, prefer_local: bool = False) -> str:
    """
    Route tasks to the most cost-effective model:
      extraction   → cheap/fast  (gpt-4o-mini or ollama)
      mapping      → cheap+smart (gpt-4o-mini)
      reasoning    → strong      (gpt-4o)
      report       → strong      (gpt-4o or claude-sonnet)
      long_doc     → claude (best long-context)
    """
    if prefer_local:
        return "ollama/llama3"

    if content_length > 15_000:
        return "claude-sonnet-4-6"          # best long-context

    routing = {
        "extraction":        "gpt-4o-mini",
        "classification":    "gpt-4o-mini",
        "mapping":           "gpt-4o-mini",
        "reasoning":         "gpt-4o",
        "report_generation": "gpt-4o",
        "fix_generation":    "gpt-4o",
        "gap_analysis":      "gpt-4o",
    }
    return routing.get(task_type, "gpt-4o-mini")


# ─── Provider Dispatch ─────────────────────────────────────────────────────────
async def call_llm(
    prompt: str,
    task_type: str,
    system: Optional[str] = None,
    model_override: Optional[str] = None,
    content_length: int = 0,
    prefer_local: bool = False,
    max_tokens: int = 2048,
) -> dict:
    """
    Universal LLM call. Returns:
      { text, model, input_tokens, output_tokens, cost_usd, latency_ms }
    """
    model = model_override or route_task(task_type, content_length, prefer_local)
    t0 = time.time()

    if model.startswith("ollama/"):
        result = await _call_ollama(prompt, system, model.split("/")[1], max_tokens)
    elif model.startswith("claude"):
        result = await _call_anthropic(prompt, system, model, max_tokens)
    else:
        result = await _call_openai(prompt, system, model, max_tokens)

    latency_ms = int((time.time() - t0) * 1000)
    cost = _estimate_cost(model, result["input_tokens"], result["output_tokens"])

    entry = {
        "task":         task_type,
        "model":        model,
        "input_tokens": result["input_tokens"],
        "output_tokens":result["output_tokens"],
        "cost_usd":     cost,
        "latency_ms":   latency_ms,
    }
    usage_log.append(entry)

    return {**result, "model": model, "cost_usd": cost, "latency_ms": latency_ms}


# ─── OpenAI ───────────────────────────────────────────────────────────────────
async def _call_openai(prompt: str, system: Optional[str], model: str, max_tokens: int) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Set it in your .env file.")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": max_tokens},
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "text":          data["choices"][0]["message"]["content"],
        "input_tokens":  data["usage"]["prompt_tokens"],
        "output_tokens": data["usage"]["completion_tokens"],
    }


# ─── Anthropic ────────────────────────────────────────────────────────────────
async def _call_anthropic(prompt: str, system: Optional[str], model: str, max_tokens: int) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Set it in your .env file.")

    body = {
        "model":      model,
        "max_tokens": max_tokens,
        "messages":   [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type":      "application/json",
            },
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "text":          data["content"][0]["text"],
        "input_tokens":  data["usage"]["input_tokens"],
        "output_tokens": data["usage"]["output_tokens"],
    }


# ─── Ollama (local, free) ─────────────────────────────────────────────────────
async def _call_ollama(prompt: str, system: Optional[str], model: str, max_tokens: int) -> dict:
    """
    Ollama must be running locally: https://ollama.com
    Install: winget install Ollama.Ollama
    Pull a model: ollama pull llama3
    """
    ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{ollama_base}/api/chat",
            json={"model": model, "messages": messages, "stream": False,
                  "options": {"num_predict": max_tokens}},
        )
        resp.raise_for_status()
        data = resp.json()

    content = data.get("message", {}).get("content", "")
    return {"text": content, "input_tokens": 0, "output_tokens": 0}


# ─── Cost Estimation ──────────────────────────────────────────────────────────
def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = MODEL_COSTS.get(model, {"input": 0.001, "output": 0.003})
    return round(
        (input_tokens / 1000) * rates["input"] +
        (output_tokens / 1000) * rates["output"],
        6
    )


def get_cost_summary() -> dict:
    total_cost = sum(e["cost_usd"] for e in usage_log)
    by_model: dict[str, dict] = {}
    for e in usage_log:
        m = e["model"]
        if m not in by_model:
            by_model[m] = {"calls": 0, "cost_usd": 0.0, "tasks": []}
        by_model[m]["calls"] += 1
        by_model[m]["cost_usd"] += e["cost_usd"]
        by_model[m]["tasks"].append(e["task"])

    # Estimate vs. single-model cost
    single_model_cost = sum(
        _estimate_cost("gpt-4o", e["input_tokens"], e["output_tokens"])
        for e in usage_log
    )
    savings_pct = round((1 - total_cost / max(single_model_cost, 0.0001)) * 100, 1)

    return {
        "total_cost_usd":     round(total_cost, 4),
        "single_model_cost":  round(single_model_cost, 4),
        "savings_pct":        savings_pct,
        "by_model":           by_model,
        "calls":              usage_log,
    }
