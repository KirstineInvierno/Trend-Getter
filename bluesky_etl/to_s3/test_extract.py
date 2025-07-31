# pylint: skip-file
import logging
from unittest.mock import MagicMock, patch
from atproto import models
from transform_oop import Message, MessageTransformer, MessageError
from extract import BlueSkyFirehose


def make_mock_commit(post_text: list[str]):
    """Function that helps make a mock Bluesky commit"""
    mock_commit = MagicMock(spec=models.ComAtprotoSyncSubscribeRepos.Commit)
    mock_commit.blocks = "test"

    mock_commit.ops = [
        MagicMock(action="create", cid="fake_cid")
    ]

    mock_raw = {"$type": "app.bsky.feed.post",
                "text": post_text}

    return mock_commit, mock_raw


def test_extract_message_logs_when_valid_message(caplog):
    post_text = "I love football"
    firehose = BlueSkyFirehose()

    with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
            patch("extract.CAR") as mock_car_func, \
            patch("extract.MessageTransformer.transform") as mock_transform, \
            patch("extract.Message") as mock_message:

        mock_commit, mock_raw = make_mock_commit(post_text)
        mock_parse_sub.return_value = mock_commit

        mock_car = MagicMock()
        mock_car.blocks.get.return_value = mock_raw
        mock_car_func.from_bytes.return_value = mock_car

        mock_transform.return_value = {"text": post_text}

        with caplog.at_level(logging.INFO):
            firehose.extract_message("test")

        assert len(caplog.records) == 1
        assert "I love football" in caplog.text


def test_extract_message_logs_when_skipping_invalid_message(caplog):
    post_text = "japanese"
    firehose = BlueSkyFirehose()

    with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
            patch("extract.CAR") as mock_car_func, \
            patch("extract.Message") as mock_message:

        mock_commit, mock_raw = make_mock_commit(post_text)
        mock_parse_sub.return_value = mock_commit

        mock_car = MagicMock()
        mock_car.blocks.get.return_value = mock_raw
        mock_car_func.from_bytes.return_value = mock_car

        mock_message.side_effect = MessageError("Message must be in english")

        with caplog.at_level(logging.ERROR):
            firehose.extract_message("test")

        assert len(caplog.records) == 1

        assert "Message skipped" in caplog.records[0].message
