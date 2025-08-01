import argparse
import logging
import pandas as pd
from pytrends.request import TrendReq

logging.basicConfig(level=logging.INFO)


def extract_trends(topics, timeframe="today 5-y", geo=""):
    pytrends = TrendReq(hl='en-GB', tz=60)  # BST not GMT
    pytrends.build_payload(
        topics, cat=0, timeframe=timeframe, geo=geo, gprop='')

    df = pytrends.interest_over_time()
    if df.empty:
        logging.warning("No data returned from Google Trends.")
        return None

    df.reset_index(inplace=True)
    df = df.drop(columns=['isPartial'], errors='ignore')
    return df


def save_to_csv(df, output_path):
    df.to_csv(output_path, index=False)
    logging.info(f"Saved trends data to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "topics", help="Comma-separated list of topics (max 5)")
    parser.add_argument("--timeframe", default="today 5-y",
                        help="Timeframe for data (e.g., 'now 7-d', 'today 1-m')")
    parser.add_argument("--geo", default="",
                        help="Geographical region code (e.g., 'GB' for UK)")
    parser.add_argument("--out", default="trends.csv", help="Output CSV file")

    args = parser.parse_args()
    topic_list = [t.strip() for t in args.topics.split(",") if t.strip()]

    if not 1 <= len(topic_list) <= 5:
        raise ValueError("Please provide between 1 and 5 topics.")

    data = extract_trends(topic_list, timeframe=args.timeframe, geo=args.geo)
    if data is not None:
        save_to_csv(data, args.out)

# CLI: python3 extract.py "Taylor Swift,Drake" --geo=GB --timeframe="now 7-d"
