"""
Transform script (OOP version):
Takes a message extracted from the API and transforms it to a 
DataFrame ready to load into the database
"""
from datetime import datetime
import pandas as pd
from transformers import pipeline

TRANSFORMER_MODEL = "finiteautomata/bertweet-base-sentiment-analysis"


class MessageTransformer:
    """Transforms API messages into DataFrames for database loading"""

    def __init__(self, sentiment_model: str = TRANSFORMER_MODEL):
        self.sentiment_model = sentiment_model
        self._sentiment_pipeline = None
        self._topics = None

    @property
    def sentiment_pipeline(self):
        """Lazy loading of sentiment analysis pipeline"""
        if self._sentiment_pipeline is None:
            self._sentiment_pipeline = pipeline(model=self.sentiment_model)
        return self._sentiment_pipeline

    @property
    def topics(self):
        """Lazy loading topics"""
        if self._topics is None:
            self._topics = ["football", "england", "spain", "cricket", "trump"]
        return self._topics

    def get_sentiment(self, text: str) -> dict:
        """
        Analyzes text sentiment using transformer model

        Returns:
            dict with label ('POS', 'NEG', 'NEU') and confidence score (0-1)
        """
        results = self.sentiment_pipeline(text)
        return max(results, key=lambda x: x.get("score"))

    def get_text(self, message: dict) -> str:
        """Extracts text content from message"""
        return """
        Cricket is so boring
        """

    def get_timestamp(self, message: dict) -> datetime:
        """Extracts timestamp from message"""
        return datetime.now()

    def find_topics_in_text(self, text: str) -> list[str] | None:
        """
        Finds which subscribed topics are mentioned in the text

        Returns:
            List of topics found, or None if no topics found
        """
        topics_found = []

        for topic in self.topics:
            if topic.lower() in text.lower():
                topics_found.append(topic)

        return topics_found if topics_found else None

    def create_dataframe(self, topic: str, sentiment: dict, timestamp: datetime) -> pd.DataFrame:
        """Creates a single-row DataFrame with the given data"""
        return pd.DataFrame({
            "topic": [topic],
            "timestamp": [timestamp],
            "sentiment_label": [sentiment.get("label")],
            "sentiment_score": [sentiment.get("score")]
        })

    def transform(self, message: dict) -> pd.DataFrame | None:
        """
        Main transformation method: converts message to DataFrame

        Args:
            message: Dictionary containing message data from API

        Returns:
            DataFrame ready for database loading, or None if no topics found
        """
        text = self.get_text(message)
        timestamp = self.get_timestamp(message)

        topics_found = self.find_topics_in_text(text)
        if not topics_found:
            return None

        sentiment = self.get_sentiment(text)

        dataframes = []
        for topic in topics_found:
            df = self.create_dataframe(topic, sentiment, timestamp)
            dataframes.append(df)

        return pd.concat(dataframes, ignore_index=True)


def main():
    """Main function"""
    transformer = MessageTransformer()
    result = transformer.transform(None)
    print(result)


if __name__ == "__main__":
    main()
