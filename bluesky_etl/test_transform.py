"""
Test file for message transformer module
"""

import pytest
import pandas as pd
import regex as re
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from transform import Message, MessageTransformer, MessageError

TOPICS_DICT = {'trump': 1, 'biden': 2}


class TestMessage:
    """Test cases for Message class"""

    def test_valid_message_creation(self):
        """Test creating a valid Message object"""
        message_dict = {
            'text': 'Test message',
            'langs': ['en'],
            '$type': 'app.bsky.feed.post',
            'createdAt': '2025-07-28T12:36:42.475Z'
        }

        message = Message(message_dict)

        assert message.text == 'Test message'
        assert message.langs == ['en']
        assert message.type == 'app.bsky.feed.post'
        assert message.timestamp == datetime.fromisoformat(
            '2025-07-28T12:36:42.475Z')

    def test_missing_required_field_raises_error(self):
        """Test that missing required fields raise MessageError"""
        incomplete_message = {
            'text': 'Test message',
            'langs': ['en'],
            # no $type or createdAt
        }

        with pytest.raises(MessageError):
            Message(incomplete_message)

    @pytest.mark.parametrize("missing_field", [
        "text", "langs", "$type", "createdAt"
    ])
    def test_each_required_field_missing(self, missing_field):
        """Test that each required field individually raises error when missing"""
        complete_message = {
            'text': 'Test message',
            'langs': ['en'],
            '$type': 'app.bsky.feed.post',
            'createdAt': '2025-07-28T12:36:42.475Z'
        }

        # remove one field
        incomplete_message = complete_message.copy()
        del incomplete_message[missing_field]

        with pytest.raises(MessageError, match=re.escape(f"Your message is missing the required field: {missing_field} ")):
            Message(incomplete_message)

    def test_timestamp_property_parsing(self):
        """Test that timestamp property correctly parses ISO string"""
        message_dict = {
            'text': 'Test message',
            'langs': ['en'],
            '$type': 'app.bsky.feed.post',
            'createdAt': '2025-07-28T12:36:42.475Z'
        }

        message = Message(message_dict)
        timestamp = message.timestamp

        assert isinstance(timestamp, datetime)
        assert timestamp.year == 2025
        assert timestamp.month == 7
        assert timestamp.day == 28
        assert timestamp.hour == 12
        assert timestamp.minute == 36
        assert timestamp.second == 42

    def test_timestamp_caching(self):
        """Test that timestamp is cached after first access"""
        message_dict = {
            'text': 'Test message',
            'langs': ['en'],
            '$type': 'app.bsky.feed.post',
            'createdAt': '2025-07-28T12:36:42.475Z'
        }

        message = Message(message_dict)

        timestamp1 = message.timestamp
        timestamp2 = message.timestamp

        assert timestamp1 is timestamp2  # same object reference


class TestMessageTransformer:
    """Test cases for MessageTransformer class"""

    @pytest.fixture
    def sample_message(self):
        """example Message object"""
        message_dict = {
            'text': 'I am trump and biden',
            'langs': ['en'],
            '$type': 'app.bsky.feed.post',
            'createdAt': '2025-07-28T12:36:42.475Z'
        }
        return Message(message_dict)

    @pytest.fixture
    def topics_df(self):
        """example topics DataFrame"""
        return pd.DataFrame({
            "topic_id": [1, 2, 3, 4, 5],
            "topic_name": ["football", "england", "spain", "cricket", "trump"]
        })

    @pytest.fixture
    def transformer(self, topics_df):
        """Fixture providing a MessageTransformer instance"""
        transformer = MessageTransformer({'trump': 1, 'biden': 2})
        # transformer._topics = topics_df  # patching the topics before it accesses the db
        return transformer

    def test_transformer_initialization(self):
        """Test MessageTransformer initialization"""
        transformer = MessageTransformer({'trump': 1, 'biden': 2})

        assert transformer.sentiment_model == "finiteautomata/bertweet-base-sentiment-analysis"
        assert transformer._sentiment_pipeline is None
        assert transformer._topics == {'trump': 1, 'biden': 2}

    def test_custom_sentiment_model(self):
        """Test MessageTransformer with custom sentiment model"""
        custom_model = "custom-sentiment-model"
        transformer = MessageTransformer(
            {'trump': 1, 'biden': 2}, sentiment_model=custom_model)

        assert transformer.sentiment_model == custom_model

    @patch('transform.pipeline')
    def test_sentiment_pipeline_lazy_loading(self, mock_pipeline, transformer):
        """Test that sentiment pipeline is lazily loaded"""
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance

        # create the pipeline
        pipeline_result = transformer.sentiment_pipeline

        mock_pipeline.assert_called_once()
        assert pipeline_result == mock_pipeline_instance

        # return cached pipeline
        pipeline_result2 = transformer.sentiment_pipeline

        # pipeline() should still only be called once
        assert mock_pipeline.call_count == 1
        assert pipeline_result2 == mock_pipeline_instance
        assert pipeline_result is pipeline_result2

    @patch('transform.pipeline')
    def test_get_sentiment(self, mock_pipeline, transformer):
        """Test sentiment analysis method"""
        # mock the pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        mock_pipeline_instance.return_value = [
            {'label': 'NEG', 'score': 0.3},
            {'label': 'POS', 'score': 0.7},
            {'label': 'NEU', 'score': 0.1}
        ]

        result = transformer.get_sentiment("I love this!")

        assert isinstance(result, dict)

        assert "label" in result
        assert result.get("label") in ["POS", "NEG", "NEU"]

        assert "score" in result
        assert 0 <= result.get("score") <= 1

        assert result == {'label': 'POS', 'score': 0.7}
        mock_pipeline_instance.assert_called_once()

    def test_find_topics_in_text(self, transformer):
        """Test topic finding in text"""

        # test with topics
        text_with_topics = "I am trump and biden"
        topics_found = transformer.find_topics_in_text(text_with_topics)

        assert 'trump' in topics_found
        assert 'biden' in topics_found
        assert len(topics_found) == 2

        # no topics
        text_without_topics = "I love cats and dogs"
        topics_found_empty = transformer.find_topics_in_text(
            text_without_topics)

        assert topics_found_empty == []

    def test_find_topics_case_insensitive(self, transformer):
        """Test that topic finding is case insensitive"""
        text = "I am TRUMP and Biden "
        topics_found = transformer.find_topics_in_text(text)

        assert 'trump' in topics_found
        assert 'biden' in topics_found
        assert len(topics_found) == 2

    def test_create_dataframe(self, transformer):
        """Test DataFrame creation"""
        sentiment = {'label': 'POS', 'score': 0.8}
        timestamp = datetime(2025, 7, 28, 12, 36, 42)

        df = transformer.create_dataframe(1, sentiment, timestamp)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]['topic_id'] == 1
        assert df.iloc[0]['sentiment_label'] == 'POS'
        assert df.iloc[0]['sentiment_score'] == 0.8
        assert df.iloc[0]['timestamp'] == timestamp

    @patch('transform.pipeline')
    def test_transform_success(self, mock_pipeline, transformer, sample_message):
        """Test successful transformation"""
        # mock sentiment pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        mock_pipeline_instance.return_value = [
            {'label': 'POS', 'score': 0.9}
        ]

        result = transformer.transform(sample_message)

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 1
        assert 'topic_id' in result.columns
        assert 'timestamp' in result.columns
        assert 'sentiment_label' in result.columns
        assert 'sentiment_score' in result.columns

    @patch('transform.pipeline')
    def test_transform_no_topics_found(self, mock_pipeline, transformer):
        """Test transformation when no topics are found"""
        message_dict = {
            'text': 'I love cats and dogs',
            'langs': ['en'],
            '$type': 'app.bsky.feed.post',
            'createdAt': '2025-07-28T12:36:42.475Z'
        }
        message = Message(message_dict)

        result = transformer.transform(message)

        assert result is None

    @patch('transform.pipeline')
    def test_transform_multiple_topics(self, mock_pipeline, transformer):
        """Test transformation with multiple topics found"""
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        mock_pipeline_instance.return_value = [
            {'label': 'POS', 'score': 0.8}
        ]

        message_dict = {
            'text': 'trump and cricket and biden',
            'langs': ['en'],
            '$type': 'app.bsky.feed.post',
            'createdAt': '2025-07-28T12:36:42.475Z'
        }
        message = Message(message_dict)

        result = transformer.transform(message)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

        topics_in_result = result['topic_id'].tolist()
        assert 1 in topics_in_result
        assert 2 in topics_in_result


class TestIntegration:
    """Integration tests"""

    @pytest.fixture
    def sample_message(self):
        """example Message object"""
        message_dict = {
            'text': 'I am  trump and i like cricket',
            'langs': ['en'],
            '$type': 'app.bsky.feed.post',
            'createdAt': '2025-07-28T12:36:42.475Z'
        }
        return Message(message_dict)

    @pytest.fixture
    def topics_df(self):
        """example topics DataFrame"""
        return pd.DataFrame({
            "topic_id": [1, 2, 3, 4, 5],
            "topic_name": ["football", "england", "spain", "cricket", "trump"]
        })

    @pytest.fixture
    def transformer(self, topics_df):
        """Fixture providing a MessageTransformer instance"""
        transformer = MessageTransformer(
            {'football': 1, 'trump': 5, 'cricket': 2})
        return transformer

    @patch('transform.pipeline')
    def test_full_pipeline_integration(self, mock_pipeline, transformer, sample_message):
        """Test the full pipeline from message creation to DataFrame output"""
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        mock_pipeline_instance.return_value = [
            {'label': 'POS', 'score': 0.85}
        ]

        result = transformer.transform(sample_message)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # trump and cricket
        assert all(result['sentiment_label'] == 'POS')
        assert all(result['sentiment_score'] == 0.85)
        assert result['topic_id'].tolist() == [5, 2]
