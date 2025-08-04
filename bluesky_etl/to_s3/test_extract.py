# pylint: skip-file
import logging
from unittest.mock import Mock, MagicMock, patch
from atproto import models
from utilities import MessageError
from extract import BlueSkyFirehose


def make_mock_commit(post_text: list[str]):
    """Function that helps make a mock Bluesky commit"""
    mock_commit = MagicMock(spec=models.ComAtprotoSyncSubscribeRepos.Commit)
    mock_commit.blocks = "test"

#         mock_commit.ops = [
#             MagicMock(action="create", cid="fake_cid")
#         ]

    mock_raw = {"$type": "app.bsky.feed.post",
                "text": post_text, "langs": langs}

#         return mock_commit, mock_raw

#     def test_extract_message_logs_when_valid_message(self, caplog):
#         post_text = "I love football"
#         firehose = BlueSkyFirehose()

#         with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
#                 patch("extract.CAR") as mock_car_func:

#             mock_commit, mock_raw = make_mock_commit(post_text)
#             mock_parse_sub.return_value = mock_commit

#             mock_car = MagicMock()
#             mock_car.blocks.get.return_value = mock_raw
#             mock_car_func.from_bytes.return_value = mock_car

#             with caplog.at_level(logging.INFO):
#                 firehose.extract_message("test")

#             assert len(caplog.records) == 1
#             assert "I love football" in caplog.text

#     def test_extract_message_logs_when_skipping_invalid_message(self, caplog):
#         post_text = "japanese"
#         firehose = BlueSkyFirehose()

#         with patch("extract.parse_subscribe_repos_message") as mock_parse_sub, \
#                 patch("extract.CAR") as mock_car_func, \
#                 patch("utilities.Message") as mock_message:

#             mock_commit, mock_raw = make_mock_commit(post_text)
#             mock_parse_sub.return_value = mock_commit

#             mock_car = MagicMock()
#             mock_car.blocks.get.return_value = mock_raw
#             mock_car_func.from_bytes.return_value = mock_car

#             mock_message.side_effect = MessageError(
#                 "Message must be in english")

#             with caplog.at_level(logging.ERROR):
#                 firehose.extract_message("test")

#             assert len(caplog.records) == 1

#             assert "Message skipped" in caplog.records[0].message


class TestHandling:

    def test_message_handler_less_than_period(self):
        with patch('load_s3.S3Loader.load_to_s3') as mock_s3_load:
            firehose = BlueSkyFirehose()
            mock_message = Mock()
            mock_message.json = {"text": "hello"}
            json_list = [{"text": "hi"}, {"text": "goodbye"}]
            assert firehose.message_handling(mock_message, json_list) == [
                {"text": "hi"}, {"text": "goodbye"}, {"text": "hello"}]
            mock_s3_load.assert_not_called()

    def test_message_handler_more_than_period(self):
        with patch('load_s3.S3Loader.load_to_s3') as mock_s3_load:
            firehose = BlueSkyFirehose()
            firehose.time_period_start = 1
            mock_message = Mock()
            mock_message.json = {"text": "hello"}
            json_list = [{"text": "hi"}, {"text": "goodbye"}]
            assert firehose.message_handling(mock_message, json_list) == []
            mock_s3_load.assert_called_once()


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
