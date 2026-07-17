"""
tests/test_cli.py
 
Integration tests that drive main.py's command handlers directly
(rather than shelling out), using a temporary data directory so
these tests never touch real data/*.json files.
"""
 
import sys
import os
import argparse
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
import pytest
import utils.storage as storage
from models import User, Project, Task
import main as cli
 
 
@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    """Point storage at a throwaway directory and reset registries per test."""
    monkeypatch.setattr(storage, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(storage, "USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr(storage, "PROJECTS_FILE", str(tmp_path / "projects.json"))
    monkeypatch.setattr(storage, "TASKS_FILE", str(tmp_path / "tasks.json"))
    User.reset()
    Project.reset()
    Task.reset()
    yield
 
 
def make_args(**kwargs):
    return argparse.Namespace(**kwargs)
 
 
def test_add_and_list_user(capsys):
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    cli.cmd_list_users(make_args())
    output = capsys.readouterr().out
    assert "Alex" in output
 
 
def test_add_project_requires_existing_user(capsys):
    with pytest.raises(SystemExit):
        cli.cmd_add_project(make_args(user="Ghost", title="X", description="", due_date=None))
    assert "no user named" in capsys.readouterr().out
 
 
def test_add_project_and_search(capsys):
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    cli.cmd_add_project(make_args(user="Alex", title="CLI Tool", description="a cli", due_date="2026-08-01"))
    cli.cmd_search_projects(make_args(user="Alex", keyword="cli"))
    output = capsys.readouterr().out
    assert "CLI Tool" in output
 
 
def test_add_task_and_complete(capsys):
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    cli.cmd_add_project(make_args(user="Alex", title="CLI Tool", description="", due_date=None))
    cli.cmd_add_task(make_args(project="CLI Tool", title="Implement add-task", assigned_to=["Alex"]))
 
    task = Task.all()[0]
    cli.cmd_complete_task(make_args(id=task.id))
    output = capsys.readouterr().out
    assert "done" in output.lower() or "Marked complete" in output
 
 
def test_persistence_round_trip(tmp_path):
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    assert os.path.exists(storage.USERS_FILE)
 
    # Simulate a fresh process by resetting and reloading from disk
    User.reset()
    Project.reset()
    Task.reset()
    cli.load_data()
 
    assert User.find_by_name("Alex") is not None
