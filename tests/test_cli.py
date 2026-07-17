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
 
 
def test_add_user_invalid_email_exits_and_writes_no_file(capsys):
    with pytest.raises(SystemExit):
        cli.cmd_add_user(make_args(name="Bad", email="not-an-email"))
    assert "Error" in capsys.readouterr().out
    # A failed add-user should not have persisted a users.json file
    assert not os.path.exists(storage.USERS_FILE)
 
 
def test_list_users_empty_shows_no_users_message(capsys):
    cli.cmd_list_users(make_args())
    assert "No users found" in capsys.readouterr().out
 
 
def test_add_task_requires_existing_project(capsys):
    with pytest.raises(SystemExit):
        cli.cmd_add_task(make_args(project="Ghost Project", title="X", assigned_to=None))
    assert "no project titled" in capsys.readouterr().out
 
 
def test_complete_task_missing_id_exits(capsys):
    with pytest.raises(SystemExit):
        cli.cmd_complete_task(make_args(id=999))
    assert "no task with id" in capsys.readouterr().out
 
 
def test_add_contributor_missing_task_exits(capsys):
    with pytest.raises(SystemExit):
        cli.cmd_add_contributor(make_args(task_id=999, user="Sam"))
    assert "no task with id" in capsys.readouterr().out
 
 
def test_search_projects_no_matches(capsys):
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    cli.cmd_add_project(make_args(user="Alex", title="CLI Tool", description="", due_date=None))
    cli.cmd_search_projects(make_args(user="Alex", keyword="nonexistent"))
    output = capsys.readouterr().out
    assert "No search results" in output or "No " in output
 
 
def test_list_projects_without_user_shows_all(capsys):
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    cli.cmd_add_user(make_args(name="Sam", email="sam@example.com"))
    cli.cmd_add_project(make_args(user="Alex", title="P1", description="", due_date=None))
    cli.cmd_add_project(make_args(user="Sam", title="P2", description="", due_date=None))
 
    cli.cmd_list_projects(make_args(user=None))
    output = capsys.readouterr().out
    assert "P1" in output
    assert "P2" in output
 
 
def test_list_projects_for_unknown_user_exits(capsys):
    with pytest.raises(SystemExit):
        cli.cmd_list_projects(make_args(user="Ghost"))
    assert "no user named" in capsys.readouterr().out
 
 
def test_list_tasks_for_project_with_no_tasks(capsys):
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    cli.cmd_add_project(make_args(user="Alex", title="Empty Project", description="", due_date=None))
    cli.cmd_list_tasks(make_args(project="Empty Project"))
    assert "No tasks for empty project found" in capsys.readouterr().out
 
 
def test_add_project_twice_for_same_user(capsys):
    # A user should be able to own multiple distinct projects.
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    cli.cmd_add_project(make_args(user="Alex", title="P1", description="", due_date=None))
    cli.cmd_add_project(make_args(user="Alex", title="P2", description="", due_date=None))
    assert len(Project.for_user(User.find_by_name("Alex").id)) == 2
 
 
def test_multiple_contributors_persist_through_reload(tmp_path):
    cli.cmd_add_user(make_args(name="Alex", email="alex@example.com"))
    cli.cmd_add_project(make_args(user="Alex", title="CLI Tool", description="", due_date=None))
    cli.cmd_add_task(make_args(project="CLI Tool", title="T1", assigned_to=["Alex"]))
    task_id = Task.all()[0].id
    cli.cmd_add_contributor(make_args(task_id=task_id, user="Sam"))
 
    User.reset()
    Project.reset()
    Task.reset()
    cli.load_data()
 
    reloaded_task = Task.find_by_id(task_id)
    assert set(reloaded_task.assigned_to) == {"Alex", "Sam"}
