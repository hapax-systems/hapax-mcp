"""HTTP client for the cockpit API."""

from __future__ import annotations

import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

BASE_URL = os.environ.get("COCKPIT_BASE_URL", "http://localhost:8051/api")
_TIMEOUT = 15.0
_SSE_TIMEOUT = 120.0
_SSE_EVENT_TIMEOUT = 30.0


def _client(timeout: float = _TIMEOUT) -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BASE_URL, timeout=timeout)


async def get(path: str, **params: str | int) -> dict:
    """GET a JSON endpoint."""
    logger.debug("GET %s params=%s", path, params or None)
    async with _client() as c:
        r = await c.get(path, params=params or None)
        r.raise_for_status()
        return r.json()


async def post(path: str, body: dict | None = None) -> dict:
    """POST to a JSON endpoint."""
    logger.debug("POST %s body=%s", path, body)
    async with _client() as c:
        r = await c.post(path, json=body)
        r.raise_for_status()
        return r.json()


async def put(path: str, body: dict | None = None) -> dict:
    """PUT to a JSON endpoint."""
    logger.debug("PUT %s body=%s", path, body)
    async with _client() as c:
        r = await c.put(path, json=body)
        r.raise_for_status()
        return r.json()


async def delete(path: str) -> dict:
    """DELETE a JSON endpoint."""
    logger.debug("DELETE %s", path)
    async with _client() as c:
        r = await c.delete(path)
        r.raise_for_status()
        return r.json()


async def post_sse(path: str, body: dict | None = None) -> str:
    """POST to an SSE endpoint, collect all text_delta/output events into a string."""
    import json as jsonlib

    logger.debug("POST SSE %s body=%s", path, body)
    chunks: list[str] = []
    current_event_type: str | None = None

    async with _client(timeout=_SSE_TIMEOUT) as c:
        async with c.stream("POST", path, json=body) as r:
            r.raise_for_status()
            async for line in _iter_lines_with_timeout(r):
                # SSE protocol: blank line ends an event block
                if not line:
                    current_event_type = None
                    continue

                # Track event type from `event:` lines
                if line.startswith("event:"):
                    current_event_type = line[6:].strip()
                    if current_event_type == "done":
                        logger.debug("SSE stream done")
                        break
                    if current_event_type == "error":
                        # Error data will follow on the next `data:` line
                        pass
                    continue

                # Parse data lines
                if line.startswith("data:"):
                    raw = line[5:].strip()
                    if current_event_type == "error":
                        logger.error("SSE error: %s", raw)
                        return f"Error: {raw}"

                    try:
                        event = jsonlib.loads(raw)
                    except (jsonlib.JSONDecodeError, ValueError):
                        continue

                    # Collect text content from various SSE event shapes
                    if "content" in event:
                        chunks.append(event["content"])
                    elif "text" in event:
                        chunks.append(event["text"])

    return "".join(chunks)


async def _iter_lines_with_timeout(
    response: httpx.Response,
    timeout: float = _SSE_EVENT_TIMEOUT,
):
    """Yield lines from an SSE stream with a per-event timeout."""
    aiter = response.aiter_lines().__aiter__()
    while True:
        try:
            line = await asyncio.wait_for(aiter.__anext__(), timeout=timeout)
            yield line
        except StopAsyncIteration:
            break
        except asyncio.TimeoutError:
            logger.error("SSE stream timed out (no event for %.0fs)", timeout)
            raise TimeoutError(
                f"SSE stream stalled — no event received for {timeout}s"
            ) from None
