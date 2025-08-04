import pytest
import regex as re
from load_s3 import S3Loader
from datetime import datetime
from unittest.mock import patch, MagicMock
import os
import json


@pytest.mark.parametrize('test_str', [
    "this",
    "an",
    "things",
    "pathological",
    "something",
])
def test_my_regex(test_str):
    assert (re.match("\w+", test_str))

def test_random_string_is_uuid():
    result = S3Loader.random_string()
    assert isinstance(result, str)
    assert len(result) == 32

@pytest.mark.parametrize("dt, expected", [
    (datetime(2025, 8, 4, 12, 30, 15),  "04-08-2025T12-30-15"),
    (datetime(2025, 12, 23, 11, 13, 25), "23-12-2025T11-13-25"),
    (datetime(2025, 10, 16, 9, 46, 59),  "16-10-2025T09-46-59"),
    (datetime(2025, 5, 3, 16, 25, 46),   "03-05-2025T16-25-46"),
    (datetime(2025, 6, 30, 14, 52, 23),  "30-06-2025T14-52-23"),
])
def test_format_date_format(dt, expected):
    result = S3Loader.format_date(dt)
    assert result == expected

