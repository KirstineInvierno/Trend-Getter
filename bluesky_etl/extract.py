"""Extract script to read live data from the Bluesky firehose API"""
from atproto import FirehoseSubscribeReposClient, parse_subscribe_repos_message, CAR, models
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class BlueSkyFirehose:
    """Tracks Bluesky messages that contain a given topic keyword"""

    def __init__(self, topic: str):
        self.topic = topic.lower()
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
                    if self.topic in post_text:
                        # Do transform  and load on each raw message extracted here. Similar to how ETL was done in Museum Kafka.
                        logging.info(raw)

    def start(self):
        """Starts the firehose stream"""
        self.client.start(self.extract_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", help="Submit a topic to track")
    args = parser.parse_args()
    firehose = BlueSkyFirehose(args.topic)
    firehose.start()
