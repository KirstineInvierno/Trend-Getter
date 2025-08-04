# pylint: skip-file
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from extract_from_s3 import S3Connection, DatabaseTopicExtractor, S3FileExtractor, Converter


class TestS3Connection:
    @patch("boto3.client")
    def test_success_logs_and_returns_client(self, mock_boto_client, caplog):
        """Test that S3Connection is successful and logs the correct message."""
        caplog.set_level("INFO")
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        conn = S3Connection()
        s3_client = conn.get_s3_connection()

        assert mock_boto_client.call_count == 1
        assert "Successfully connected to AWS S3." in caplog.text
        assert s3_client == mock_client

    @patch("boto3.client", side_effect=ConnectionError("Unable to connect to AWS S3"))
    def test_failure_logs_and_sets_none(self, mock_boto_client, caplog):
        """Test that S3Connection logs an error and sets client to None on failure."""
        conn = S3Connection()
        s3_client = conn.get_s3_connection()

        assert "Unable to connect to AWS S3" in caplog.text
        assert s3_client is None


class TestDatabaseTopicExtractor:
    def test_get_topics_dict_from_rds_success(self, caplog, test_data):
        """Test successful retrieval of topics from RDS and correct log messages."""
        caplog.set_level("INFO")

        mock_conn = MagicMock()
        mock_loader = MagicMock()
        mock_loader.get_sql_conn.return_value = mock_conn

        with patch("pandas.read_sql", return_value=test_data):
            extractor = DatabaseTopicExtractor()
            result = extractor.get_topics_dict_from_rds(mock_loader)

        expected = {"test1": "id1", "test2": "id2"}
        assert result == expected
        assert "Successfully connected to RDS." in caplog.text
        assert "Retrieved" in caplog.text

    def test_get_topics_dict_from_rds_connection_error(self, caplog):
        """Test that a connection error to RDS returns an empty dict and logs an error."""
        caplog.set_level("ERROR")
        mock_loader = MagicMock()
        mock_loader.get_sql_conn.side_effect = ConnectionError("Unable to connect to RDS")

        extractor = DatabaseTopicExtractor()
        result = extractor.get_topics_dict_from_rds(mock_loader)

        assert result == {}
        assert "Unable to connect to RDS" in caplog.text


class TestS3FileExtractor:
    def test_get_latest_file_key(self, fake_s3_client):
        """Test that the latest file key is correctly identified by S3FileExtractor."""
        extractor = S3FileExtractor(fake_s3_client)
        latest_key = extractor.get_latest_file_key("fake-bucket")
        assert latest_key == "file2.json"

    def test_raises_error_on_empty_bucket(self, fake_s3_client):
        """Test that S3FileExtractor raises FileNotFoundError when no files exist in the bucket."""
        fake_s3_client.list_objects_v2.return_value = {"Contents": []}
        extractor = S3FileExtractor(fake_s3_client)

        with pytest.raises(FileNotFoundError):
            extractor.get_latest_file_key("fake-bucket")


class TestConverter:
    def test_get_latest_file_as_dicts(self, fake_s3_client, caplog):
        """Test that the Converter retrieves and converts the latest file content to a list of dicts."""
        caplog.set_level("INFO")
        extractor = S3FileExtractor(fake_s3_client)
        converter = Converter(extractor)
        dicts = converter.get_latest_file_as_dicts("fake-bucket")

        assert "JSON file successfully converted." in caplog.text
        assert isinstance(dicts, list)
        assert dicts[0]["text"] == "hello"


class TestTransformer:
    def test_transform_messages_into_dataframe(self, fake_dataframe, sample_message):
        """Test that the transformer converts a message into a DataFrame."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = fake_dataframe

        result = mock_transformer.transform(sample_message, mock_transformer)

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "topic_id" in result.columns
        assert "sentiment_label" in result.columns