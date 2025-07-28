"""Extract script to read live data from the Bluesky firehose API"""
from atproto import FirehoseSubscribeReposClient, parse_subscribe_repos_message, CAR, models
import argparse


def firehose_stream(topic: str):
    """Wrapper function that creates a message handler to filters posts by a given topic."""

    def firehose(message):
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
                    if topic in post_text:
                        # Do transform  and load on each raw message here. Similar to how ETL was done in Museum Kafka
                        print(raw)
    return firehose


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", help="Submit a topic to track")
    args = parser.parse_args()
    client = FirehoseSubscribeReposClient()
    client.start(firehose_stream(args.topic))
