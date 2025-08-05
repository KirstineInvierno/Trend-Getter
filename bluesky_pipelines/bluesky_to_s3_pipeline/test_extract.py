# pylint: skip-file
from extract import BlueSkyFirehose
import logging
from unittest.mock import MagicMock, patch
from atproto import models


def make_mock_commit(post_text: list[str], lang: str):
    """Function that helps make a mock Bluesky commit"""
    mock_commit = MagicMock(spec=models.ComAtprotoSyncSubscribeRepos.Commit)
    mock_commit.blocks = "test"

    mock_commit.ops = [
        MagicMock(action="create", cid="fake_cid")
    ]

    mock_raw = {"$type": "app.bsky.feed.post",
                "text": post_text, "langs": [lang], "createdAt": "2022-05-12"}

    return mock_commit, mock_raw


def test_extract_message_logs_when_valid_message(caplog):
    post_text = "I love football"
    firehose = BlueSkyFirehose()

    with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
            patch("extract.CAR") as mock_car_func, \
            patch("extract.S3Loader.load_to_s3") as mock_s3_loader:

        mock_commit, mock_raw = make_mock_commit(post_text, "en")
        mock_parse_sub.return_value = mock_commit

        mock_car = MagicMock()
        mock_car.blocks.get.return_value = mock_raw
        mock_car_func.from_bytes.return_value = mock_car

        with caplog.at_level(logging.INFO):
            firehose.extract_message("fake_message")

        assert "English message found" in caplog.records[0].message


def test_extract_message_logs_when_skipping_invalid_message(caplog):
    post_text = "japanese"
    firehose = BlueSkyFirehose()

    with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
            patch("extract.CAR") as mock_car_func:

        mock_commit, mock_raw = make_mock_commit(post_text, "jp")
        mock_parse_sub.return_value = mock_commit

        mock_car = MagicMock()
        mock_car.blocks.get.return_value = mock_raw
        mock_car_func.from_bytes.return_value = mock_car

        with caplog.at_level(logging.INFO):
            firehose.extract_message("fake_message")

        assert "English message found" not in caplog.records
