from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "server"))

from server.my_app.utils.negative_terms import normalize_negative_terms


def test_normalize_negative_terms_string():
    assert normalize_negative_terms("  hello world  ") == "hello world"


def test_normalize_negative_terms_list():
    assert (
        normalize_negative_terms(["  foo", "bar ", " baz"]) == "foo, bar, baz"
    )


def test_normalize_negative_terms_none():
    assert normalize_negative_terms(None) == ""
    assert normalize_negative_terms("") == ""
    assert normalize_negative_terms([]) == ""


def test_normalize_negative_terms_list_and_string_equivalence():
    terms_list = ["cat", "dog"]
    terms_str = "cat, dog"
    assert normalize_negative_terms(terms_list) == normalize_negative_terms(terms_str)

