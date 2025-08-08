from datetime import datetime
import regex as re
import pytest
from pandas import DataFrame
from threshold_check import DataGetter, ThresholdChecker
from threshold_ses import Sender


class TestTCheck:

    def test_get_now(self):
        getter = DataGetter()
        assert isinstance(getter.get_now(), datetime)

    def test_get_ten_minutes_ago(self):
        getter = DataGetter()
        ten_ago = getter.get_ten_minutes_ago()
        print(ten_ago)
        assert isinstance(ten_ago, str)
        assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", ten_ago)

    @pytest.fixture
    def threshold_dict(self):
        return {
            "topic_id": 5,
            "threshold": 5
        }

    @pytest.fixture
    def threshold_dict_2(self):
        return {
            "topic_id": 2,
            "threshold": 18
        }

    @pytest.fixture
    def mentions_df(self):
        return DataFrame({
            "topic_id": [5, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 3]
        }).reset_index(names="mention_id")

    def test_check_threshold(self, threshold_dict, threshold_dict_2, mentions_df):
        checker = ThresholdChecker()
        assert checker.check_threshold(threshold_dict, mentions_df) == 8
        assert checker.check_threshold(threshold_dict_2, mentions_df) == False


class TestSes:
    def test_create_email_from_dict(self):
        sender = Sender()
        subscription_dict = {
            "topic_name": "trump",
            "threshold": 100,
            "mention_count": 8000000
        }
        result = sender.create_email_from_dict(subscription_dict)
        assert all(key in result for key in [
            "subject",
            "text",
            "html"
        ])
        assert all(tag in result.get("html")for tag in [
            "<html>",
            "<head>",
            "</body>",
            "<body>"
        ])
        assert result.get("subject") == "Activity Spike relating to trump"
