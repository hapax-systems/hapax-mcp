"""HTTP client for the cockpit API."""

from __future__ import annotations

import os

import httpx

BASE_URL = os.environ.get("COCKPIT_BASE_URL", "http://localhost:8051/api")
_TIMEOUT = 15.0


def _headers() -> dict[str, str]:
    """Build request headers, including Bearer auth when COCKPIT_API_KEY is set."""
    headers: dict[str, str] = {}
    api_key = os.environ.get("COCKPIT_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BASE_URL, timeout=_TIMEOUT, headers=_headers())


async def get(path: str, **params: str | int) -> dict:
    """GET a JSON endpoint."""
    async with _client() as c:
        r = await c.get(path, params=params or None)
        r.raise_for_status()
        return r.json()


async def post(path: str, body: dict | None = None) -> dict:
    """POST to a JSON endpoint."""
    async with _client() as c:
        r = await c.post(path, json=body)
        r.raise_for_status()
        return r.json()


async def put(path: str, body: dict | None = None) -> dict:
    """PUT to a JSON endpoint."""
    async with _client() as c:
        r = await c.put(path, json=body)
        r.raise_for_status()
        return r.json()


async def delete(path: str) -> dict:
    """DELETE a JSON endpoint."""
    async with _client() as c:
        r = await c.delete(path)
        r.raise_for_status()
        return r.json()


async def post_sse(
    path: str,
    body: dict | None = None,
    *,
    max_chunks: int = 1000,
    max_total_bytes: int = 1_048_576,
) -> str:
    """POST to an SSE endpoint, collect all text_delta/output events into a string.

    Accumulation stops when *max_chunks* events or *max_total_bytes* of text
    have been collected, whichever comes first.
    """
    import json as jsonlib

    chunks: list[str] = []
    total_bytes = 0
    truncated = False
    async with _client() as c:
        async with c.stream("POST", path, json=body) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line.startswith("data: "):
                    continue
                try:
                    event = jsonlib.loads(line[6:])
                except (jsonlib.JSONDecodeError, ValueError):
                    continue
                # Collect text content from various SSE event shapes
                text: str | None = None
                if "content" in event:
                    text = event["content"]
                elif "text" in event:
                    text = event["text"]
                elif event.get("event") == "done":
                    break
                elif event.get("event") == "error":
                    return f"Error: {event.get('data', event)}"

                if text is not None:
                    chunks.append(text)
                    total_bytes += len(text.encode())
                    if len(chunks) >= max_chunks or total_bytes >= max_total_bytes:
                        truncated = True
                        break

    result = "".join(chunks)
    if truncated:
        result += "\n\n[truncated — response exceeded accumulation limits]"
    return result
