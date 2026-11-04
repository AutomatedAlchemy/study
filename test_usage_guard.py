"""Offline tests for usage_guard: no request leaves the machine."""
import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("study_usage_guard", HERE / "usage_guard.py")
ug = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ug)


def _creds(tmp_path, monkeypatch, **oauth):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    path = tmp_path / ".credentials.json"
    path.write_text(json.dumps({"claudeAiOauth": oauth, "other": 1}))
    os.chmod(path, 0o600)
    return path


def test_peak_counts_session_and_weekly_but_not_a_model_scoped_limit():
    usage = {"limits": [{"kind": "session", "percent": 12},
                        {"kind": "weekly_all", "percent": 91},
                        {"kind": "weekly_scoped", "percent": 100}]}
    assert ug.peak_percent(usage) == 91


def test_peak_falls_back_to_the_window_fields():
    usage = {"five_hour": {"utilization": 30.0}, "seven_day": {"utilization": 88.5}}
    assert ug.peak_percent(usage) == 88.5
    assert ug.peak_percent({}) is None


def test_a_valid_token_is_used_without_a_refresh(tmp_path, monkeypatch):
    _creds(tmp_path, monkeypatch, accessToken="a1", refreshToken="r1", expiresAt=10_000_000)
    monkeypatch.setattr(ug, "_post_json", lambda *a: (_ for _ in ()).throw(AssertionError("refresh")))
    assert ug.access_token(now_ms=1_000) == "a1"


def test_an_expired_token_is_refreshed_and_written_back(tmp_path, monkeypatch):
    path = _creds(tmp_path, monkeypatch, accessToken="old", refreshToken="r1",
                  expiresAt=500, scopes=["user:inference", "user:profile"])
    sent = {}

    def post(url, payload):
        sent.update(url=url, payload=payload)
        return {"access_token": "new", "refresh_token": "r2", "expires_in": 3600}

    monkeypatch.setattr(ug, "_post_json", post)
    assert ug.access_token(now_ms=1_000) == "new"
    assert sent["payload"] == {"grant_type": "refresh_token", "refresh_token": "r1",
                               "client_id": ug.CLIENT_ID, "scope": "user:inference user:profile"}
    saved = json.loads(path.read_text())
    assert saved["other"] == 1
    assert saved["claudeAiOauth"]["accessToken"] == "new"
    assert saved["claudeAiOauth"]["refreshToken"] == "r2"
    assert saved["claudeAiOauth"]["expiresAt"] == 1_000 + 3_600_000
    assert oct(path.stat().st_mode & 0o777) == "0o600"


def test_a_failed_refresh_leaves_the_file_alone(tmp_path, monkeypatch):
    path = _creds(tmp_path, monkeypatch, accessToken="old", refreshToken="r1", expiresAt=500)
    before = path.read_text()
    monkeypatch.setattr(ug, "_post_json", lambda *a: (_ for _ in ()).throw(OSError("offline")))
    assert ug.access_token(now_ms=1_000) is None
    assert ug.current_percent() is None
    assert path.read_text() == before


def test_no_credentials_means_unknown(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    assert ug.current_percent() is None
