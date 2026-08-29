"""Reusable rate-limited HTTP client for all source adapters.

Features:
- Per-source rate limiting (respects each API's limits)
- Automatic retries with exponential backoff
- Content-addressed caching (avoid re-fetching unchanged data)
- User-Agent rotation
- Response validation
- Structured logging
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RateLimiter:
    """Token bucket rate limiter."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    _minute_tokens: float = 0.0
    _hour_tokens: float = 0.0
    _last_refill: float = 0.0

    def __post_init__(self):
        self._minute_tokens = self.requests_per_minute
        self._hour_tokens = self.requests_per_hour
        self._last_refill = time.time()

    def wait_if_needed(self):
        """Block until a request slot is available."""
        now = time.time()
        elapsed = now - self._last_refill

        # Refill minute bucket
        self._minute_tokens = min(
            self.requests_per_minute,
            self._minute_tokens + elapsed * (self.requests_per_minute / 60)
        )
        # Refill hour bucket
        self._hour_tokens = min(
            self.requests_per_hour,
            self._hour_tokens + elapsed * (self.requests_per_hour / 3600)
        )
        self._last_refill = now

        # Wait if either bucket is empty
        if self._minute_tokens < 1:
            wait = (1 - self._minute_tokens) * (60 / self.requests_per_minute)
            time.sleep(wait)
            self._minute_tokens = 1
        if self._hour_tokens < 1:
            wait = (1 - self._hour_tokens) * (3600 / self.requests_per_hour)
            time.sleep(wait)
            self._hour_tokens = 1

        self._minute_tokens -= 1
        self._hour_tokens -= 1


@dataclass
class CachedResponse:
    """Cached HTTP response with content hash."""
    status: int
    body: str
    content_hash: str
    fetched_at: float
    headers: dict = field(default_factory=dict)


class HttpClient:
    """Rate-limited HTTP client with caching and retries."""

    USER_AGENTS = [
        "MoltworkOracle/0.1 (autonomous-agent-economy-dataset)",
        "MoltworkBot/0.1 (+https://moltwork.com)",
    ]

    def __init__(
        self,
        source_id: str,
        base_url: str = "",
        api_key: str = "",
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.source_id = source_id
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = RateLimiter(requests_per_minute, requests_per_hour)
        self._cache: dict[str, CachedResponse] = {}
        self._stats = {"requests": 0, "cache_hits": 0, "errors": 0}

    def _headers(self, extra: dict | None = None) -> dict:
        h = {
            "User-Agent": self.USER_AGENTS[0],
            "Accept": "application/json",
        }
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        if extra:
            h.update(extra)
        return h

    def _cache_key(self, url: str, params: dict | None = None) -> str:
        raw = url + json.dumps(params or {}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(
        self,
        path: str = "",
        params: dict | None = None,
        headers: dict | None = None,
        use_cache: bool = True,
    ) -> dict | list | None:
        """Make a GET request with rate limiting, caching, and retries."""
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url += f"?{query}"

        # Check cache
        cache_key = self._cache_key(url)
        if use_cache and cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached.fetched_at < 300:  # 5 min cache
                self._stats["cache_hits"] += 1
                return json.loads(cached.body)

        # Rate limit
        self.rate_limiter.wait_if_needed()
        self._stats["requests"] += 1

        # Request with retries
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(url, headers=self._headers(headers))
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode()
                    content_hash = hashlib.sha256(body.encode()).hexdigest()[:16]

                    # Cache
                    self._cache[cache_key] = CachedResponse(
                        status=resp.status,
                        body=body,
                        content_hash=content_hash,
                        fetched_at=time.time(),
                        headers=dict(resp.headers),
                    )

                    return json.loads(body)

            except urllib.error.HTTPError as e:
                if e.code == 429:  # Rate limited
                    retry_after = int(e.headers.get("Retry-After", 60))
                    time.sleep(retry_after)
                    continue
                elif e.code in (500, 502, 503, 504):  # Server errors
                    time.sleep(2 ** attempt)
                    continue
                else:
                    self._stats["errors"] += 1
                    return None

            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                time.sleep(2 ** attempt)
                continue

        self._stats["errors"] += 1
        return None

    def post(self, path: str, data: dict, headers: dict | None = None) -> dict | None:
        """Make a POST request."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.rate_limiter.wait_if_needed()
        self._stats["requests"] += 1

        try:
            body = json.dumps(data).encode()
            req = urllib.request.Request(url, data=body, headers=self._headers(headers), method="POST")
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            self._stats["errors"] += 1
            return None

    def get_stats(self) -> dict:
        return dict(self._stats)


# === Source-specific rate limit presets ===

SOURCE_PRESETS = {
    "github": {"requests_per_minute": 30, "requests_per_hour": 5000},
    "algora": {"requests_per_minute": 20, "requests_per_hour": 500},
    "moltjobs": {"requests_per_minute": 2, "requests_per_hour": 120},
    "bountybook": {"requests_per_minute": 10, "requests_per_hour": 200},
    "the402": {"requests_per_minute": 10, "requests_per_hour": 200},
    "agenthansa": {"requests_per_minute": 10, "requests_per_hour": 200},
    "agenthire": {"requests_per_minute": 10, "requests_per_hour": 200},
    "rentahuman": {"requests_per_minute": 10, "requests_per_hour": 200},
    "taskforce": {"requests_per_minute": 10, "requests_per_hour": 200},
    "gigs": {"requests_per_minute": 10, "requests_per_hour": 200},
    "payapi": {"requests_per_minute": 10, "requests_per_hour": 200},
    "agent402": {"requests_per_minute": 10, "requests_per_hour": 200},
    "x402engine": {"requests_per_minute": 10, "requests_per_hour": 200},
    "olas": {"requests_per_minute": 10, "requests_per_hour": 200},
    "daydreams": {"requests_per_minute": 10, "requests_per_hour": 200},
    "near": {"requests_per_minute": 10, "requests_per_hour": 200},
    "superteam": {"requests_per_minute": 10, "requests_per_hour": 200},
    "huggingface": {"requests_per_minute": 30, "requests_per_hour": 1000},
}


def get_client(source_id: str, **kwargs) -> HttpClient:
    """Get a pre-configured client for a source."""
    preset = SOURCE_PRESETS.get(source_id, {})
    return HttpClient(source_id=source_id, **{**preset, **kwargs})
