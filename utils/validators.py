"""
utils/validators.py
 
Small standalone validation helpers used by the CLI layer before
data ever reaches the model classes. Keeping these separate from
models/ means they can be reused (and unit-tested) independently.
"""
 
import re
from datetime import datetime
 
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
 
 
def is_valid_email(email):
    """Return True if `email` looks like a syntactically valid email."""
    return bool(email) and bool(EMAIL_RE.match(email))
 
 
def is_valid_date(date_str):
    """Return True if `date_str` is None/empty or matches YYYY-MM-DD."""
    if not date_str:
        return True
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
 
 
def non_empty(value, field_name="value"):
    """Raise a friendly ValueError if `value` is empty/blank."""
    if not value or not str(value).strip():
        raise ValueError(f"{field_name} cannot be empty")
    return str(value).strip()
