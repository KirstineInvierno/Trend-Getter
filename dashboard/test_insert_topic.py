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
    
    @patch("insert_topic.Connection")
    def test_insert_topic_executes_query(self, mock_connection_class):
        """Test that a topic is inserted into the database."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_class.return_value.get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        inserter = TopicInserter()

        inserter.insert_topic("testtopic")

        mock_cursor.execute.assert_called_once_with(
            """INSERT INTO bluesky.topic (topic_name)
                                VALUES (%s)
                                ON CONFLICT (topic_name) DO NOTHING;""",
            ("testtopic",)
        )
        mock_conn.close.assert_called_once()

    @patch("insert_topic.Connection")
    def test_insert_duplicate_topic_does_not_error(self, mock_connection_class):
        """Test that inserting the same topic twice does not raise an error and executes the query twice."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_class.return_value.get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        inserter = TopicInserter()

        inserter.insert_topic("testtopic")
        inserter.insert_topic("testtopic")

        query = """INSERT INTO bluesky.topic (topic_name)
                                VALUES (%s)
                                ON CONFLICT (topic_name) DO NOTHING;"""
        expected_args = ("testtopic",)

        assert mock_cursor.execute.call_count == 2
        mock_cursor.execute.assert_called_with(query, expected_args)

    @patch("insert_topic.Connection.get_connection")
    def test_insert_new_topic(self, mock_get_conn):
        """Tests that a new topic is added into the database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [None, (123,)]

        inserter = TopicInserter()

        result = inserter.insert_topic("liverpool ")

        assert result == 123
        assert mock_cursor.execute.call_count == 2

    @patch("insert_topic.Connection.get_connection")
    def test_insert_existing_topic(self, mock_get_conn):
        """Tests that an existing topic is returned from the database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (1,)

        inserter = TopicInserter()

        result = inserter.insert_topic("liverpool ")

        assert result == 1
        assert mock_cursor.execute.call_count == 1
