"""Extract script to read live data from the Bluesky firehose API"""
import logging
from atproto import FirehoseSubscribeReposClient, parse_subscribe_repos_message, CAR, models
from utilities import Message
from load_s3 import S3Loader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class BlueSkyFirehose:
    """Tracks all Bluesky messages"""

    def __init__(self) -> None:
        self.client = FirehoseSubscribeReposClient()

    def extract_message(self, message) -> None:
        """Reads a message from the stream and prints the raw output if it is a post"""

        commit = parse_subscribe_repos_message(message)

        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            return

        car = CAR.from_bytes(commit.blocks)

        for op in commit.ops:
            if op.action == "create" and op.cid:
                raw_message = car.blocks.get(op.cid)
                if not raw_message:
                    continue
                if raw_message.get("$type") == "app.bsky.feed.post" \
                    and raw_message.get("langs") \
                        and "en" in raw_message.get("langs"):
                    message_obj = Message(raw_message)
                    S3Loader.load_to_s3(message_obj)

    def start(self) -> None:
        """Starts the firehose stream"""
        self.client.start(self.extract_message)


if __name__ == "__main__":
    firehose = BlueSkyFirehose()
    firehose.start()
