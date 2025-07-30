# pylint: skip-file
import logging
from unittest.mock import MagicMock, patch
from atproto import models

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


def test_extract_message_logs_when_topic_found(caplog):
    topics = ["football"]
    post_text = "love football"
    firehose = BlueSkyFirehose(topics)

    with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
            patch("extract.CAR") as mock_car_func:

        mock_commit, mock_raw = make_mock_commit(post_text)
        mock_parse_sub.return_value = mock_commit

        mock_car = MagicMock()
        mock_car.blocks.get.return_value = mock_raw
        mock_car_func.from_bytes.return_value = mock_car

        with caplog.at_level(logging.INFO):
            firehose.extract_message("test")

        assert len(caplog.records) == 1
        assert topics[0] in caplog.text


def test_dont_extract_message_logs_when_topic_not_found(caplog):
    topics = ["life"]
    post_text = "i love football"
    firehose = BlueSkyFirehose(topics)

    with patch("extract.parse_subscribe_repos_message") as mock_parse, \
            patch("extract.CAR") as mock_car_func:

        mock_commit, mock_raw = make_mock_commit(post_text)
        mock_parse.return_value = mock_commit

        mock_car = MagicMock()
        mock_car.blocks.get.return_value = mock_raw
        mock_car_func.from_bytes.return_value = mock_car

        with caplog.at_level(logging.INFO):
            firehose.extract_message("test")

        assert len(caplog.records) == 0
        assert topics[0] not in caplog.text
