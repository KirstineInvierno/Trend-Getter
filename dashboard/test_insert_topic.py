# pylint: skip-file

import pytest
from insert_topic import TopicInserter, Connection
from unittest.mock import patch, MagicMock
from typing import Any

inserter = TopicInserter()
conn = Connection()

class TestConnection():
    """Tests for the Connection class handling database connections."""
    @patch("psycopg2.connect", side_effect=Exception("Connection error"))
    def test_db_connection_failure_raises_exception(self, mock_connect: MagicMock, caplog: Any) -> None:
        """Test that an exception during database connection is raised and an error is logged."""
        caplog.set_level("INFO")
        with pytest.raises(Exception):
            conn.get_connection()
        assert "Database connection failed" in caplog.text

    @patch("psycopg2.connect")
    def test_db_connection_logs_success(self, mock_connect: MagicMock, caplog: Any) -> None:
        """Test that a successful database connection logs the expected message."""
        caplog.set_level("INFO")
        conn.get_connection()
        assert mock_connect.call_count == 1
        assert "Successfully connected." in caplog.text

class TestTopicInserter():
    """Tests for the TopicInserter class handling topic formatting."""
    def test_format_topic_with_spaces(self) -> None:
        """Test that format_topic removes whitespace."""
        assert inserter.format_topic("  chocolate ") == "chocolate"
        assert inserter.format_topic("watch ") == "watch"
        assert inserter.format_topic(" perfume") == "perfume"

    def test_invalid_topics(self) -> None:
        """Test that format_topic raises ValueError on empty or invalid input."""
        with pytest.raises(ValueError):
            inserter.format_topic("")
            inserter.format_topic(" ")
            inserter.format_topic(" a")
            inserter.format_topic("q")

    def test_format_topic_with_capitalisation(self) -> None:
        """Test that format_topic converts topics to lowercase."""
        assert inserter.format_topic("CHocoLate") == "chocolate"
        assert inserter.format_topic("WATCH") == "watch"
        assert inserter.format_topic("Perfume") == "perfume"
