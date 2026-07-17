"""
models/project.py
 
Defines the Project class. A Project belongs to exactly one User
(one-to-many: User -> Projects) and can contain many Tasks
(one-to-many: Project -> Tasks).
"""
 
from datetime import datetime
 
 
class Project:
    """
    Represents a project owned by a single user.
 
    Class attributes:
        _id_counter: auto-incrementing id assigned to each new Project.
        _registry:   in-memory collection of every Project, keyed by id.
    """
 
    _id_counter = 1
    _registry = {}
 
    def __init__(self, title, description, due_date, user_id, project_id=None):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.user_id = user_id
 
        if project_id is None:
            self.id = Project._id_counter
            Project._id_counter += 1
        else:
            self.id = project_id
            Project._id_counter = max(Project._id_counter, project_id + 1)
 
        self.task_ids = []  # one-to-many: Project -> Tasks
        Project._registry[self.id] = self
 
    @property
    def title(self):
        return self._title
 
    @title.setter
    def title(self, value):
        if not value or not str(value).strip():
            raise ValueError("project title cannot be empty")
        self._title = str(value).strip()
 
    @property
    def due_date(self):
        return self._due_date
 
    @due_date.setter
    def due_date(self, value):
        """Accepts None or a string in YYYY-MM-DD format."""
        if value is None or value == "":
            self._due_date = None
            return
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(
                f"due_date must be in YYYY-MM-DD format, got {value!r}"
            ) from exc
        self._due_date = value
 
    def add_task(self, task):
        """Attach a Task's id to this project (one-to-many relationship)."""
        if task.id not in self.task_ids:
            self.task_ids.append(task.id)
 
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "user_id": self.user_id,
            "task_ids": self.task_ids,
        }
 
    @classmethod
    def from_dict(cls, data):
        project = cls(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            user_id=data["user_id"],
            project_id=data["id"],
        )
        project.task_ids = data.get("task_ids", [])
        return project
 
    @classmethod
    def all(cls):
        return [cls._registry[k] for k in sorted(cls._registry)]
 
    @classmethod
    def find_by_title(cls, title):
        title = title.strip().lower()
        for project in cls._registry.values():
            if project.title.lower() == title:
                return project
        return None
 
    @classmethod
    def find_by_id(cls, project_id):
        return cls._registry.get(project_id)
 
    @classmethod
    def for_user(cls, user_id):
        """Return all projects belonging to a given user id."""
        return [p for p in cls.all() if p.user_id == user_id]
 
    @classmethod
    def reset(cls):
        cls._registry = {}
        cls._id_counter = 1
 
    def __str__(self):
        due = self.due_date or "no due date"
        return f"[{self.id}] {self.title} (due {due}) - {len(self.task_ids)} task(s)"
 
    def __repr__(self):
        return f"Project(id={self.id}, title={self.title!r}, user_id={self.user_id})"
