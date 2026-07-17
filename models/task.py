"""
models/task.py
 
Defines the Task class. A Task belongs to one Project, but can also
have multiple contributors (many-to-many: Project/Task <-> Users via
assigned_to list), satisfying the many-to-many relationship requirement.
"""
 
VALID_STATUSES = ("todo", "in-progress", "done")
 
 
class Task:
    """
    Represents a single task belonging to a project.
 
    Class attributes:
        _id_counter: auto-incrementing id assigned to each new Task.
        _registry:   in-memory collection of every Task, keyed by id.
    """
 
    _id_counter = 1
    _registry = {}
 
    def __init__(self, title, project_id, assigned_to=None, status="todo", task_id=None):
        self.title = title
        self.project_id = project_id
        self.assigned_to = assigned_to or []  # many-to-many: task <-> contributors
        self.status = status
 
        if task_id is None:
            self.id = Task._id_counter
            Task._id_counter += 1
        else:
            self.id = task_id
            Task._id_counter = max(Task._id_counter, task_id + 1)
 
        Task._registry[self.id] = self
 
    @property
    def title(self):
        return self._title
 
    @title.setter
    def title(self, value):
        if not value or not str(value).strip():
            raise ValueError("task title cannot be empty")
        self._title = str(value).strip()
 
    @property
    def status(self):
        return self._status
 
    @status.setter
    def status(self, value):
        if value not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}, got {value!r}")
        self._status = value
 
    def mark_complete(self):
        self.status = "done"
 
    def add_contributor(self, user_name):
        """Add another contributor to this task (many-to-many relationship)."""
        if user_name not in self.assigned_to:
            self.assigned_to.append(user_name)
 
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "project_id": self.project_id,
            "assigned_to": self.assigned_to,
            "status": self.status,
        }
 
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            project_id=data["project_id"],
            assigned_to=data.get("assigned_to", []),
            status=data.get("status", "todo"),
            task_id=data["id"],
        )
 
    @classmethod
    def all(cls):
        return [cls._registry[k] for k in sorted(cls._registry)]
 
    @classmethod
    def find_by_id(cls, task_id):
        return cls._registry.get(task_id)
 
    @classmethod
    def for_project(cls, project_id):
        return [t for t in cls.all() if t.project_id == project_id]
 
    @classmethod
    def reset(cls):
        cls._registry = {}
        cls._id_counter = 1
 
    def __str__(self):
        who = ", ".join(self.assigned_to) if self.assigned_to else "unassigned"
        return f"[{self.id}] {self.title} ({self.status}) - {who}"
 
    def __repr__(self):
        return f"Task(id={self.id}, title={self.title!r}, status={self.status!r})"
