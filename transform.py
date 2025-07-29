from datetime import datetime
import pandas as pd
from transformers import pipeline


sentiment = pipeline(
    model="finiteautomata/bertweet-base-sentiment-analysis")


def get_sentiment(text):
    return max(sentiment(text), key=lambda x: x.get("score"))


def get_text(message):
    return "BBC Radio 1\nNewsbeat @ 12:45\n\nEngland's Lionesses go back-to-back as they win the Women's Euros for the second time, beating Spain on penalties in Switzerland."


def get_timestamp(message):
    return datetime.now()


def get_topics():
    return ["football", "england", "spain", "cricket", "trump"]


def topics_in_text(text, topics):
    topics_in = []
    for topic in topics:
        if topic.lower() in text.lower():
            topics_in.append(topic)

    return topics_in


def make_df(topic, sentiment, timestamp):

    df = pd.DataFrame({
        "topic": [topic],
        "timestamp": [timestamp],
        "sentiment_label": [sentiment.get("label")],
        "sentiment_score": [sentiment.get("score")]
    })
    return df


def transform(message):
    text = get_text(message)
    timestamp = get_timestamp(message)

    topics = get_topics()
    topics_in = topics_in_text(text, topics)
    sentiment = get_sentiment(text)

    dfs = []

    for topic in topics_in:
        dfs.append(make_df(topic, sentiment, timestamp))

    return pd.concat(dfs, ignore_index=True)


def main():
    # text = "I'll stick with The SNP. Don't need a new centre left party run from England for England competing for votes in Scotland thanks."
    # print(get_sentiment(text))

    print(transform(None))


if __name__ == "__main__":
    main()
