"""
tests/test_validators.py
 
Unit tests for utils/validators.py — these are pure functions with
no model or file dependencies, so they're tested in isolation.
"""
 
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
import pytest
from utils.validators import is_valid_email, is_valid_date, non_empty
 
 
@pytest.mark.parametrize("email", [
    "alex@example.com",
    "a.b+tag@sub.example.co.ke",
    "x@y.io",
])
def test_is_valid_email_accepts_good_addresses(email):
    assert is_valid_email(email) is True
 
 
@pytest.mark.parametrize("email", [
    "",
    None,
    "not-an-email",
    "missing-at.com",
    "double@@example.com",
    "no-domain@",
    "spaces in@example.com",
])
def test_is_valid_email_rejects_bad_addresses(email):
    assert is_valid_email(email) is False
 
 
@pytest.mark.parametrize("date_str", [
    None,
    "",
    "2026-01-01",
    "2026-12-31",
])
def test_is_valid_date_accepts_good_dates(date_str):
    assert is_valid_date(date_str) is True
 
 
@pytest.mark.parametrize("date_str", [
    "not-a-date",
    "2026/01/01",
    "01-01-2026",
    "2026-13-40",
])
def test_is_valid_date_rejects_bad_dates(date_str):
    assert is_valid_date(date_str) is False
 
 
def test_non_empty_returns_stripped_value():
    assert non_empty("  Alex  ", "name") == "Alex"
 
 
@pytest.mark.parametrize("value", ["", "   ", None])
def test_non_empty_raises_on_blank(value):
    with pytest.raises(ValueError):
        non_empty(value, "name")
 
 
def test_non_empty_error_message_includes_field_name():
    with pytest.raises(ValueError, match="email"):
        non_empty("", "email")
