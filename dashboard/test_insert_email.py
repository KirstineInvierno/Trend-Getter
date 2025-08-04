# pylint: skip-file

import pytest
from insert_email import EmailInserter
from unittest.mock import patch, MagicMock
from typing import Any

inserter = EmailInserter()


def setup_mock_db(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_get_conn.return_value = mock_conn
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn, mock_cursor


class TestEmailInserter():
    """Tests for the EmailInserter class"""

    @patch("insert_email.Connection.get_connection")
    def test_get_user_id(self, mock_get_conn) -> None:
        mock_conn, mock_cursor = setup_mock_db(mock_get_conn)

        mock_cursor.fetchone.return_value = (1,)

        assert inserter.get_user_id("nahim_mail@mail.com") == 1

    @patch("insert_email.Connection.get_connection")
    def test_get_invalid_user_id(self, mock_get_conn) -> None:
        mock_conn, mock_cursor = setup_mock_db(mock_get_conn)

        mock_cursor.fetchone.return_value = (-1,)

        assert inserter.get_user_id("nahim_mail@mail.com") == -1

    @patch("insert_email.Connection.get_connection")
    def test_insert_email(self, mock_get_conn) -> None:
        mock_conn, mock_cursor = setup_mock_db(mock_get_conn)

        mock_cursor.fetchone.side_effect = [None, (1,)]

        result = inserter.insert_email("nahim_mail@mail.com")

        assert result == 1
        assert mock_cursor.execute.call_count == 2

    @patch("insert_email.Connection.get_connection")
    def test_email_exists(self, mock_get_conn) -> None:
        mock_conn, mock_cursor = setup_mock_db(mock_get_conn)

        mock_cursor.fetchone.side_effect = [(1,)]

        result = inserter.insert_email("nahim_mail@mail.com")

        assert result == 1
        assert mock_cursor.execute.call_count == 1
