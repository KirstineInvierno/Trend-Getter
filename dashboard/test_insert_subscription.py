# pylint: skip-file

import pytest
from insert_subscription import SubscriptionInserter
from unittest.mock import patch, MagicMock


inserter = SubscriptionInserter()


class TestSubscriptionInserter():
    """Tests for the SubscriptionInserter class"""

    @patch("insert_subscription.Connection.get_connection")
    def test_insert_new_subscription(self, mock_get_conn) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None
        result = inserter.insert_subscription(1, 2)
        assert result is True

    @patch("insert_subscription.Connection.get_connection")
    def test_insert_existing_subscription(self, mock_get_conn) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = [(1,)]
        result = inserter.insert_subscription(1, 2)
        assert result is False

    @patch("insert_subscription.Connection.get_connection")
    def test_get_subscriptions(self, mock_get_conn) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [("liverpool",), ("arsenal",)]

        result = inserter.get_subscriptions(1)
        assert result == ["liverpool", "arsenal"]

    @patch("insert_subscription.Connection.get_connection")
    def test_unsubscribe_success(self, mock_get_conn) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.rowcount = 1
        result = inserter.unsubscribe(1, "Tech")
        assert result is True

    @patch("insert_subscription.Connection.get_connection")
    def test_unsubscribe_from_non_existing_subscription(self, mock_get_conn) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.rowcount = 0

        result = inserter.unsubscribe(1, "fake_topic")
        assert result is False
