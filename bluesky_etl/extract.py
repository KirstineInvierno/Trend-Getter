"""Extract script to read live data from the Bluesky firehose API"""
import argparse
import logging
from atproto import FirehoseSubscribeReposClient, parse_subscribe_repos_message, CAR, models


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class BlueSkyFirehose:
    """Tracks Bluesky messages that contain a given topic keyword"""

    def __init__(self, topics: str):
        self.topics = [topic.lower() for topic in topics]
        self.client = FirehoseSubscribeReposClient()

    def extract_message(self, message):
        """Reads a message from the stream and prints the raw output if it is a post"""

        commit = parse_subscribe_repos_message(message)

        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            return

        car = CAR.from_bytes(commit.blocks)

        for op in commit.ops:
            if op.action == "create" and op.cid:
                raw = car.blocks.get(op.cid)
                if not raw:
                    continue
                if raw.get("$type") == "app.bsky.feed.post":
                    post_text = raw.get("text").lower()
                    if any(topic in post_text for topic in self.topics):
                        # Do transform  and load on each raw message extracted here.
                        # Similar to how ETL was done in Museum Kafka.
                        logging.info(raw)

    def start(self):
        """Starts the firehose stream"""
        self.client.start(self.extract_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "topics", help="Submit topics to track, separated by commas")
    args = parser.parse_args()
    topics = [topic.strip() for topic in args.topics.split(",")]
    firehose = BlueSkyFirehose(topics)
    firehose.start()
