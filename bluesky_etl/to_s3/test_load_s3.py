import pytest
import regex as re


@pytest.mark.parametrize('test_str', [
    "this",
    "an",
    "things",
    "pathological",
    "something",
])
def test_my_regex(test_str):
    assert (re.match("\w+", test_str))
