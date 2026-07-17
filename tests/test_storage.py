"""
tests/test_storage.py
 
Unit tests for utils/storage.py — verifies save/load round-trips and,
importantly, that missing or malformed JSON files never crash the
tool (they should degrade to an empty list with a warning instead).
"""
 
import sys
import os
import json
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
import pytest
from utils import storage
 
 
def test_load_json_missing_file_returns_empty_list(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    assert storage.load_json(str(missing)) == []
 
 
def test_load_json_empty_file_returns_empty_list(tmp_path):
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("")
    assert storage.load_json(str(empty_file)) == []
 
 
def test_load_json_malformed_file_returns_empty_list_with_warning(tmp_path, capsys):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json,,,")
    result = storage.load_json(str(bad_file))
    assert result == []
    assert "Warning" in capsys.readouterr().out
 
 
def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "users.json"
    records = [{"id": 1, "name": "Alex", "email": "alex@example.com"}]
    storage.save_json(str(path), records)
    loaded = storage.load_json(str(path))
    assert loaded == records
 
 
def test_save_json_creates_parent_directory(tmp_path):
    nested_path = tmp_path / "nested" / "deeper" / "users.json"
    storage.save_json(str(nested_path), [{"id": 1}])
    assert nested_path.exists()
    assert json.loads(nested_path.read_text()) == [{"id": 1}]
 
 
def test_save_json_pretty_prints(tmp_path):
    path = tmp_path / "users.json"
    storage.save_json(str(path), [{"id": 1, "name": "Alex"}])
    content = path.read_text()
    # Pretty-printed JSON should be multi-line, not a single compact line
    assert content.count("\n") > 1
 
 
def test_load_all_uses_configured_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr(storage, "PROJECTS_FILE", str(tmp_path / "projects.json"))
    monkeypatch.setattr(storage, "TASKS_FILE", str(tmp_path / "tasks.json"))
 
    storage.save_json(str(tmp_path / "users.json"), [{"id": 1, "name": "Alex"}])
 
    result = storage.load_all()
    assert result["users"] == [{"id": 1, "name": "Alex"}]
    assert result["projects"] == []
    assert result["tasks"] == []
