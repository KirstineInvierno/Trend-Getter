"""
transform script:
takes a message extracted from the API and transforms it to a 
DataFrame ready to load into the database
"""
from datetime import datetime
import pandas as pd
from transformers import pipeline


def get_sentiment(text: str) -> dict:
    """
    Uses an LLM to analyse a text snippet and suggest its sentiment
    returns a dict with:
        label - 'POS', 'NEG' or 'NEU'
        score - certainty score from 0-1 (float)

    uses finiteautomata/bertweet-base-sentiment-analysis model which
    is finetuned for tweets
    """
    sentiment = pipeline(
        model="finiteautomata/bertweet-base-sentiment-analysis")
    return max(sentiment(text), key=lambda x: x.get("score"))


def get_text(message: dict) -> str:
    """extracts the text from a message that was posted"""
    return """
    BBC Radio 1
    Newsbeat @ 12:45
    
    England's Lionesses go back-to-back as they win the Women's Euros for \
        the second time, beating Spain on penalties in Switzerland.
    """


def get_timestamp(message: dict) -> datetime:
    """extracts the timestamp from a message that was posted"""
    return datetime.now()


def get_topics() -> list[str]:
    """
    returns a list of topics subscribed to by users 
    (will need to access db for this in final version)
    """
    return ["football", "england", "spain", "cricket", "trump"]


def topics_in_text(text: str, topics: list[str]) -> list[str] | None:
    """
    deciphers which topics from a given list of topics are 
    in a given string

    in a future version could add LLM zero-shot classification functionality
    """
    topics_in = []
    for topic in topics:
        if topic.lower() in text.lower():
            topics_in.append(topic)

    if len(topics_in) < 1:
        return None

    return topics_in


def make_df(topic: str, sentiment: dict, timestamp: datetime) -> pd.DataFrame:
    """creates DataFrame with data in the right format for loading"""

    df = pd.DataFrame({
        "topic": [topic],
        "timestamp": [timestamp],
        "sentiment_label": [sentiment.get("label")],
        "sentiment_score": [sentiment.get("score")]
    })
    return df


def transform(message: dict) -> pd.DataFrame:
    """
    takes a message extracted from the API and transforms it to a 
    DataFrame ready to load into the database
    """
    text = get_text(message)
    timestamp = get_timestamp(message)

    topics = get_topics()
    topics_in = topics_in_text(text, topics)
    if not topics_in:
        return None
    sentiment = get_sentiment(text)

    dfs = []

    for topic in topics_in:
        dfs.append(make_df(topic, sentiment, timestamp))

    return pd.concat(dfs, ignore_index=True)


def main():
    """main function"""
    print(transform(None))


if __name__ == "__main__":
    main()
