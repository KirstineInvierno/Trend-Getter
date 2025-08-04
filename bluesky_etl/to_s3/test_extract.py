# pylint: skip-file
import logging
from unittest.mock import Mock, MagicMock, patch
from atproto import models
from utilities import MessageError
from extract import BlueSkyFirehose


def make_mock_commit(post_text: list[str], langs: list[str]):
    """Function that helps make a mock Bluesky commit"""
    mock_commit = MagicMock(spec=models.ComAtprotoSyncSubscribeRepos.Commit)
    mock_commit.blocks = "test"

    mock_raw = {"$type": "app.bsky.feed.post",
                "text": post_text, "langs": langs}

    return mock_commit, mock_raw


class TestHandling:

    def test_message_handler_less_than_period(self):
        with patch('load_s3.S3Loader.load_to_s3') as mock_s3_load:
            firehose = BlueSkyFirehose()
            mock_message = Mock()
            mock_message.json = {"text": "hello"}
            firehose.json_list = [{"text": "hi"}, {"text": "goodbye"}]
            assert firehose.message_handling(mock_message) == False
            assert firehose.json_list == [{"text": "hi"}, {
                "text": "goodbye"}, {"text": "hello"}]
            mock_s3_load.assert_not_called()

    def test_message_handler_more_than_period(self):
        with patch('load_s3.S3Loader.load_to_s3') as mock_s3_load:
            firehose = BlueSkyFirehose()
            firehose.time_period_start = 1
            mock_message = Mock()
            mock_message.json = {"text": "hello"}
            firehose.json_list = [{"text": "hi"}, {"text": "goodbye"}]
            assert firehose.message_handling(mock_message) == True
            assert firehose.json_list == []
            mock_s3_load.assert_called_once()


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
