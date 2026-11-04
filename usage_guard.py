"""Read the Claude subscription usage the way Claude Code's `/usage` does.

The menu asks for one number: the highest percent across the session (5 h)
window and the all-models weekly window. Model-scoped weekly limits (e.g. a
Fable-only allowance) are left out, they do not stop a Sonnet session.

The access token in ``~/.claude/.credentials.json`` lives a few hours; on a
host where Claude has not run since then it is stale. It is refreshed here with
the same request Claude Code sends (endpoint and client id taken from its
2.1.316 binary) and written back in place, so Claude Code keeps working with
the rotated refresh token.

Every failure (no credentials, offline, an API change) returns None: the caller
decides what an unknown usage means.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
import urllib.request
from pathlib import Path

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
TOKEN_URL = "https://platform.claude.com/v1/oauth/token"
CLIENT_ID = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
_BETA = "oauth-2025-04-20"
_TIMEOUT = 8
# Refresh a little before the stored expiry, so the usage call cannot race it.
_EXPIRY_MARGIN_MS = 60_000
_COUNTED_KINDS = ("session", "weekly_all")


def _credentials_path() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return Path(base) / ".credentials.json"


def _post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.load(resp)


def _get_json(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                               "anthropic-beta": _BETA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.load(resp)


def _write_credentials(path: Path, data: dict) -> None:
    """Atomic replace that keeps the file's 0600 mode."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".credentials.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def access_token(now_ms: "int | None" = None) -> "str | None":
    """A valid access token, refreshed and saved first when the stored one expired."""
    path = _credentials_path()
    try:
        data = json.loads(path.read_text())
        oauth = data["claudeAiOauth"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    now_ms = int(time.time() * 1000) if now_ms is None else now_ms
    if int(oauth.get("expiresAt") or 0) - _EXPIRY_MARGIN_MS > now_ms:
        return oauth.get("accessToken")
    refresh = oauth.get("refreshToken")
    if not refresh:
        return None
    payload = {"grant_type": "refresh_token", "refresh_token": refresh, "client_id": CLIENT_ID}
    if oauth.get("scopes"):
        payload["scope"] = " ".join(oauth["scopes"])
    try:
        fresh = _post_json(TOKEN_URL, payload)
    except (OSError, ValueError):
        return None
    token = fresh.get("access_token")
    if not token:
        return None
    oauth["accessToken"] = token
    if fresh.get("refresh_token"):
        oauth["refreshToken"] = fresh["refresh_token"]
    if fresh.get("expires_in"):
        oauth["expiresAt"] = now_ms + int(fresh["expires_in"]) * 1000
    try:
        _write_credentials(path, data)
    except OSError:
        pass   # the token still works for this call
    return token


def peak_percent(usage: dict) -> "float | None":
    """Highest percent of the session and all-models weekly limits in a usage reply."""
    limits = usage.get("limits")
    if isinstance(limits, list):
        values = [float(lim["percent"]) for lim in limits
                  if isinstance(lim, dict) and lim.get("kind") in _COUNTED_KINDS
                  and lim.get("percent") is not None]
        if values:
            return max(values)
    values = [float(usage[key]["utilization"]) for key in ("five_hour", "seven_day")
              if isinstance(usage.get(key), dict) and usage[key].get("utilization") is not None]
    return max(values) if values else None


def current_percent() -> "float | None":
    """The peak usage percent right now, or None when it cannot be read."""
    token = access_token()
    if not token:
        return None
    try:
        return peak_percent(_get_json(USAGE_URL, token))
    except (OSError, ValueError):
        return None
