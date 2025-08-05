import pytest
import regex as re
from load_s3 import S3Loader, BUCKET_NAME, FILE_PATH
from datetime import datetime
from unittest.mock import patch, MagicMock
import logging
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

@patch("load_s3.S3Loader.random_string", return_value="abcd")
@patch("load_s3.S3Loader.format_date", return_value="04-08-2025T15-45-26")
def test_download_json_creates_expected_file_and_logs(mock_date, mock_uuid, tmp_path, caplog):
    test_data = [{"msg": "hello"}]
    expected_filename = "abcd--04-08-2025T15-45-26.json"
    expected_path = tmp_path / expected_filename

    with patch("builtins.open", lambda f, mode, encoding=None: (tmp_path / f).open(mode, encoding=encoding)):
        with caplog.at_level("INFO"):
            filename = S3Loader.download_json(test_data)

    assert expected_path.exists()
    assert f"{expected_filename} saved" in caplog.text

@patch("load_s3.S3Loader.random_string", return_value="abcd")
@patch("load_s3.S3Loader.format_date", return_value="04-08-2025T15-45-26")
@patch("load_s3.boto3.Session")
def test_load_to_s3_uploads_file_and_logs(mock_session, mock_format_date, mock_random_string, caplog):
    test_data = [{"msg": "hello"}]
    expected_filename = "abcd--04-08-2025T15-45-26.json"
    fake_client = MagicMock()
    mock_session.return_value.client.return_value = fake_client

    with caplog.at_level(logging.INFO):
        filename = S3Loader.load_to_s3(test_data)

    assert filename == expected_filename

    fake_client.put_object.assert_called_once_with(
        Bucket=BUCKET_NAME,
        Key=f"{FILE_PATH}{expected_filename}",
        Body=json.dumps(test_data),
        ContentType="application/json"
    )

    assert f"{expected_filename} uploaded to {BUCKET_NAME}" in caplog.text