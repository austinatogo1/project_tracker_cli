"""
tests/test_models.py
 
Unit tests for the User, Project, and Task classes.
Run with: pytest
"""
 
import pytest
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from models import User, Project, Task
 
 
@pytest.fixture(autouse=True)
def reset_registries():
    """Ensure every test starts with clean class-level registries."""
    User.reset()
    Project.reset()
    Task.reset()
    yield
 
 
def test_create_user():
    user = User(name="Alex", email="alex@example.com")
    assert user.name == "Alex"
    assert user.email == "alex@example.com"
    assert user.id == 1
 
 
def test_user_invalid_email_raises():
    with pytest.raises(ValueError):
        User(name="Bad Email", email="not-an-email")
 
 
def test_user_empty_name_raises():
    with pytest.raises(ValueError):
        User(name="   ", email="x@example.com")
 
 
def test_user_find_by_name_case_insensitive():
    User(name="Alex", email="alex@example.com")
    found = User.find_by_name("alex")
    assert found is not None
    assert found.name == "Alex"
 
 
def test_create_project_linked_to_user():
    user = User(name="Alex", email="alex@example.com")
    project = Project(title="CLI Tool", description="desc", due_date="2026-08-01", user_id=user.id)
    user.add_project(project)
    assert project.user_id == user.id
    assert project.id in user.project_ids
 
 
def test_project_invalid_due_date_raises():
    user = User(name="Alex", email="alex@example.com")
    with pytest.raises(ValueError):
        Project(title="Bad Date", description="", due_date="not-a-date", user_id=user.id)
 
 
def test_project_for_user():
    user = User(name="Alex", email="alex@example.com")
    other = User(name="Sam", email="sam@example.com")
    Project(title="P1", description="", due_date=None, user_id=user.id)
    Project(title="P2", description="", due_date=None, user_id=other.id)
    assert len(Project.for_user(user.id)) == 1
    assert Project.for_user(user.id)[0].title == "P1"
 
 
def test_create_task_linked_to_project():
    user = User(name="Alex", email="alex@example.com")
    project = Project(title="CLI Tool", description="", due_date=None, user_id=user.id)
    task = Task(title="Implement add-task", project_id=project.id, assigned_to=["Alex"])
    project.add_task(task)
    assert task.project_id == project.id
    assert task.id in project.task_ids
    assert task.status == "todo"
 
 
def test_task_mark_complete():
    project = Project(title="P", description="", due_date=None, user_id=1)
    task = Task(title="T", project_id=project.id)
    task.mark_complete()
    assert task.status == "done"
 
 
def test_task_invalid_status_raises():
    with pytest.raises(ValueError):
        Task(title="T", project_id=1, status="not-a-status")
 
 
def test_task_add_contributor_many_to_many():
    task = Task(title="T", project_id=1, assigned_to=["Alex"])
    task.add_contributor("Sam")
    assert set(task.assigned_to) == {"Alex", "Sam"}
    # Adding the same contributor twice should not duplicate them
    task.add_contributor("Sam")
    assert task.assigned_to.count("Sam") == 1
 
 
def test_round_trip_serialization():
    user = User(name="Alex", email="alex@example.com")
    data = user.to_dict()
    User.reset()
    rebuilt = User.from_dict(data)
    assert rebuilt.name == "Alex"
    assert rebuilt.email == "alex@example.com"
    assert rebuilt.id == data["id"]
