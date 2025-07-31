# pylint: skip-file
import logging
from unittest.mock import MagicMock, patch
from atproto import models
from utilities import MessageError
from extract import BlueSkyFirehose


def make_mock_commit(post_text: str, langs: list[str]):
    """Function that helps make a mock Bluesky commit"""
    mock_commit = MagicMock(spec=models.ComAtprotoSyncSubscribeRepos.Commit)
    mock_commit.blocks = "test"

    mock_commit.ops = [
        MagicMock(action="create", cid="fake_cid")
    ]

    mock_raw = {"$type": "app.bsky.feed.post",
                "text": post_text, "langs": langs}

    return mock_commit, mock_raw


def test_extract_message_logs_when_valid_language(caplog):
    post_text = "I love football"
    firehose = BlueSkyFirehose()

    with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
            patch("extract.CAR") as mock_car_func, \
            patch("extract.Message") as mock_message, \
            patch("extract.S3Loader.load_to_s3") as mock_loader:

        mock_commit, mock_raw = make_mock_commit(post_text, ["en"])
        mock_parse_sub.return_value = mock_commit

        mock_car = MagicMock()
        mock_car.blocks.get.return_value = mock_raw
        mock_car_func.from_bytes.return_value = mock_car

        with caplog.at_level(logging.INFO):
            firehose.extract_message("test")

        assert mock_loader.call_count == 1


def test_dont_extract_message_logs_when_invalid_language(caplog):
    post_text = "japanese"
    firehose = BlueSkyFirehose()

    with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
            patch("extract.CAR") as mock_car_func, \
            patch("extract.Message") as mock_message, \
            patch("extract.S3Loader.load_to_s3") as mock_loader:

        mock_commit, mock_raw = make_mock_commit(post_text, ["jp"])
        mock_parse_sub.return_value = mock_commit

        mock_car = MagicMock()
        mock_car.blocks.get.return_value = mock_raw
        mock_car_func.from_bytes.return_value = mock_car

        with caplog.at_level(logging.INFO):
            firehose.extract_message("test")

        assert mock_loader.call_count == 0


def test_start_calls_client():
    firehose = BlueSkyFirehose()
    with patch.object(firehose.client, "start") as mock_start:
        firehose.start()
    assert mock_start.call_count == 1


def test_extraction_skips_without_commit(caplog):
    firehose = BlueSkyFirehose()
    with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
            patch("extract.CAR") as mock_car_func:

        with caplog.at_level(logging.INFO):
            firehose.extract_message("no commit")

        assert mock_parse_sub.call_count == 1
        assert mock_car_func.call_count == 0
