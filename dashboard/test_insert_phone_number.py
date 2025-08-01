# pylint: skip-file

import pytest
from insert_phone_number import PhoneNumberInserter
from unittest.mock import patch, MagicMock
from typing import Any

inserter = PhoneNumberInserter()


class TestNumberInserter():
    """Tests for the TopicInserter class handling topic formatting."""

    @patch("insert_phone_number.Connection.get_connection")
    def test_get_user_id(self, mock_get_conn) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (1,)

        assert inserter.get_user_id("07599095847") == 1

    @patch("insert_phone_number.Connection.get_connection")
    def test_get_invalid_user_id(self, mock_get_conn) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (-1,)

        assert inserter.get_user_id("07599095847") == -1

    @patch("insert_phone_number.Connection.get_connection")
    def test_insert_phone_number(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [None, (1,)]

        result = inserter.insert_number("07599093847")

        assert result == 1
        assert mock_cursor.execute.call_count == 2

    @patch("insert_phone_number.Connection.get_connection")
    def test_phone_number_exists(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [(1,)]

        result = inserter.insert_number("07599093847")

        assert result == 1
        assert mock_cursor.execute.call_count == 1
