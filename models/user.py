"""
models/user.py
 
Defines the Person base class and the User class that inherits from it.
Demonstrates inheritance, encapsulation (via @property), and class-level
ID tracking / object registries.
"""
 
import re
 
 
class Person:
    """
    Base class representing a generic person.
 
    This exists so `User` (and any future person-like entity, e.g. Admin)
    can inherit shared identity behavior instead of duplicating it.
    """
 
    def __init__(self, name):
        self.name = name
 
    @property
    def name(self):
        return self._name
 
    @name.setter
    def name(self, value):
        if not value or not str(value).strip():
            raise ValueError("name cannot be empty")
        self._name = str(value).strip()
 
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"
 
 
class User(Person):
    """
    A User of the project tracker system.
 
    Class attributes:
        _id_counter: auto-incrementing id assigned to each new User.
        _registry:   in-memory collection of every User created/loaded,
                     keyed by id, so we can look users up by name/id.
    """
 
    _id_counter = 1
    _registry = {}
 
    def __init__(self, name, email, user_id=None):
        super().__init__(name)
        self.email = email
        if user_id is None:
            self.id = User._id_counter
            User._id_counter += 1
        else:
            self.id = user_id
            # Keep the counter ahead of any explicitly-provided id
            # (this happens when we reload users from disk).
            User._id_counter = max(User._id_counter, user_id + 1)
 
        self.project_ids = []  # one-to-many: User -> Projects (stored by id)
        User._registry[self.id] = self
 
    @property
    def email(self):
        return self._email
 
    @email.setter
    def email(self, value):
        if not value or "@" not in str(value):
            raise ValueError(f"invalid email: {value!r}")
        self._email = str(value).strip()
 
    def add_project(self, project):
        """Attach a Project's id to this user (one-to-many relationship)."""
        if project.id not in self.project_ids:
            self.project_ids.append(project.id)
 
    def to_dict(self):
        """Serialize this User to a plain dict for JSON persistence."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "project_ids": self.project_ids,
        }
 
    @classmethod
    def from_dict(cls, data):
        """Rebuild a User instance from a dict loaded from JSON."""
        user = cls(name=data["name"], email=data["email"], user_id=data["id"])
        user.project_ids = data.get("project_ids", [])
        return user
 
    @classmethod
    def all(cls):
        """Return all known users (sorted by id) as a list."""
        return [cls._registry[k] for k in sorted(cls._registry)]
 
    @classmethod
    def find_by_name(cls, name):
        """Case-insensitive lookup of a user by name."""
        name = name.strip().lower()
        for user in cls._registry.values():
            if user.name.lower() == name:
                return user
        return None
 
    @classmethod
    def find_by_id(cls, user_id):
        return cls._registry.get(user_id)
 
    @classmethod
    def reset(cls):
        """Clear the in-memory registry (used before loading from disk)."""
        cls._registry = {}
        cls._id_counter = 1
 
    def __str__(self):
        return f"[{self.id}] {self.name} <{self.email}> ({len(self.project_ids)} project(s))"
 
    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r})"
