"""HTTP client for the cockpit API."""

from __future__ import annotations

import os

import httpx

BASE_URL = os.environ.get("COCKPIT_BASE_URL", "http://localhost:8051/api")
_TIMEOUT = 15.0


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BASE_URL, timeout=_TIMEOUT)


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


async def post_sse(path: str, body: dict | None = None) -> str:
    """POST to an SSE endpoint, collect all text_delta/output events into a string."""
    import json as jsonlib

    chunks: list[str] = []
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
                if "content" in event:
                    chunks.append(event["content"])
                elif "text" in event:
                    chunks.append(event["text"])
                elif event.get("event") == "done":
                    break
                elif event.get("event") == "error":
                    return f"Error: {event.get('data', event)}"
    return "".join(chunks)
