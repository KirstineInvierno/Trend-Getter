"""
Transform script:
Takes a message extracted from the API and transforms it to a 
DataFrame ready to load into the database
"""

# pylint: disable=W1203

from datetime import datetime
import time
import logging
import pandas as pd
from transformers import pipeline
from collections.abc import Callable


TRANSFORMER_MODEL = "finiteautomata/bertweet-base-sentiment-analysis"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class MessageError(Exception):
    """Error for when creating Message object"""
    pass


class Message:
    """message recieved from API"""

    def __init__(self, message_dict: dict):
        self._validation(message_dict)

        self.text = message_dict.get("text")
        self.langs = message_dict.get("langs")
        self.type = message_dict.get("$type")
        self._timestamp = None
        self._timestamp_string = message_dict.get("createdAt")

    def _validation(self, message_dict: dict):
        required_fields = [
            "text",
            "langs",
            "$type",
            "createdAt"
        ]

        for field in required_fields:
            if field not in message_dict:
                raise MessageError(
                    f"Your message is missing the required field: {field} ")
        if "en" not in message_dict["langs"]:
            raise MessageError(
                f"Message must be in english ")

    @property
    def timestamp(self) -> datetime:
        """Extracts timestamp from message"""
        if self._timestamp is None:
            temp_timestamp = self._timestamp_string
            self._timestamp = datetime.fromisoformat(temp_timestamp)

        return self._timestamp


class MessageTransformer:
    """Transforms API messages into DataFrames for database loading"""

    def __init__(self, topics_dict: dict, sentiment_model: str = TRANSFORMER_MODEL):
        self.sentiment_model = sentiment_model
        self._sentiment_pipeline = None
        self._topics = topics_dict

    @property
    def sentiment_pipeline(self) -> Callable:
        """Lazy loading of sentiment analysis pipeline"""
        if self._sentiment_pipeline is None:
            self._sentiment_pipeline = pipeline(model=self.sentiment_model)
        return self._sentiment_pipeline

    def get_sentiment(self, text: str) -> dict:
        """
        Analyzes text sentiment using transformer model

        Returns:
            dict with label ('POS', 'NEG', 'NEU') and confidence score (0-1)
        """
        logging.info("Running sentiment analysis...")
        time1 = time.time()
        llm_pipeline = self.sentiment_pipeline
        sentiments = llm_pipeline(text)  # separated to appease pylint
        time2 = time.time()
        logging.info(
            f"Sentiment analysis complete in {round(time2-time1, 2)} seconds")
        return max(sentiments, key=lambda sentiment: sentiment.get("score"))

    def find_topics_in_text(self, text: str) -> list[str]:
        """
        Finds which subscribed topics are mentioned in the text

        Returns:
            List of topics found, or None if no topics found
        """
        logging.info("Matching topics in topics list...")
        topics_found = []

        for topic in self._topics.keys():
            if topic.lower() in text.lower():
                topics_found.append(topic)

        return topics_found

    def create_dataframe(self, topic_id: str, sentiment: dict, timestamp: datetime) -> pd.DataFrame:
        """Creates a single-row DataFrame with the given data"""
        logging.info("Creating DataFrame...")
        return pd.DataFrame({
            "topic_id": [topic_id],
            "timestamp": [timestamp],
            "sentiment_label": [sentiment.get("label")],
            "sentiment_score": [sentiment.get("score")]
        })

    def transform(self, message: Message) -> pd.DataFrame | None:
        """
        Main transformation method: converts message to DataFrame

        Args:
            message: Dictionary containing message data from API

        Returns:
            DataFrame ready for database loading, or None if no topics found
        """
        time1 = time.time()
        logging.info("Begin transform script")
        topics_found = self.find_topics_in_text(message.text)
        if not topics_found:
            logging.error("No matching topics found, returning None")
            return None

        sentiment = self.get_sentiment(message.text)

        dataframes = []
        for topic in topics_found:
            df = self.create_dataframe(
                self._topics[topic], sentiment, message.timestamp)
            dataframes.append(df)

        time2 = time.time()
        logging.info(
            f"transform script complete in {round(time2-time1, 2)} seconds")

        return pd.concat(dataframes, ignore_index=True)


def main():
    """Main function"""
    message = Message({
        'text': 'I love donald trump',
        'langs': ['en'],
        '$type': 'app.bsky.feed.post',
        'reply': {
            'root': {
                'cid': 'bafyreidcbtn7o3q5eksnj2qt5bff2glucf2wbwt6yo3zd4nzarneweibs4',
                'uri': 'at://did:plc:4llrhdclvdlmmynkwsmg5tdc/app.bsky.feed.post/3luzluujzah2m'
            },
            'parent': {
                'cid': 'bafyreidcbtn7o3q5eksnj2qt5bff2glucf2wbwt6yo3zd4nzarneweibs4',
                'uri': 'at://did:plc:4llrhdclvdlmmynkwsmg5tdc/app.bsky.feed.post/3luzluujzah2m'
            }
        },
        'createdAt': '2025-07-28T12:36:42.475Z'
    })
    transformer = MessageTransformer()
    result = transformer.transform(message)
    print(result)


if __name__ == "__main__":
    main()
