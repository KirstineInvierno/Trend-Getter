import pytest
import pandas as pd
from unittest.mock import MagicMock

@pytest.fixture
def fake_s3_client():
    mock = MagicMock()

    mock.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "file1.json", "LastModified": 1},
            {"Key": "file2.json", "LastModified": 2},
        ]
    }

    mock.get_object.return_value = {
        "Body": MagicMock(read=MagicMock(return_value=b'[{"text":"hello","langs":["en"],"$type":"post","createdAt":"2025-08-04T12:23:52"}]'))
    }
    return mock

@pytest.fixture
def test_data():
    return pd.DataFrame({"topic_name": ["test1", "test2"], "topic_id": ["id1", "id2"]})

@pytest.fixture
def test_json():
    sample_jsons = [
        {"text": "Hello"},
        {"text": "World"},
    ]
    return sample_jsons

@pytest.fixture
def sample_message():
    return {
        "text": "hello, it is Monday",
        "langs": ["en"],
        "$type": "post",
        "createdAt": "2025-08-04T12:23:52"
    }

@pytest.fixture
def fake_dataframe():
    return pd.DataFrame({
        "topic_id": ["123"],
        "timestamp": [pd.Timestamp("2025-08-04")],
        "sentiment_label": ["POS"],
        "sentiment_score": [0.9532]
    })
