"""
models package
 
Exposes the core domain classes so they can be imported as:
    from models import User, Project, Task, Person
"""
 
from .user import Person, User
from .project import Project
from .task import Task
 
__all__ = ["Person", "User", "Project", "Task"]
