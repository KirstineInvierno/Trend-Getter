"""Extract script to read live data from the Bluesky firehose API"""
import time
import logging
from atproto import FirehoseSubscribeReposClient, parse_subscribe_repos_message, CAR, models
from utilities import Message
from load_s3 import S3Loader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

TIME_PERIOD_LENGTH = 600  # seconds


class BlueSkyFirehose:
    """Tracks all Bluesky messages"""

    def __init__(self) -> None:
        """its tuesday innit"""
        self.client = FirehoseSubscribeReposClient()
        self.time_period_start = time.time()
        self.json_list = []

    def message_handling(self, message: Message) -> bool:
        """
        manages the messages, if it's been 10 minutes since last 
        upload (time_period_start) then upload current batch of 
        jsons and reset json_list if not then just add the new message 
        json to the list
        """
        self.json_list.append(message.json)
        current_time = time.time()
        if current_time-self.time_period_start < TIME_PERIOD_LENGTH:
            return False
        S3Loader.load_to_s3(self.json_list)
        # S3Loader.download_json(self.json_list)
        self.time_period_start = current_time
        self.json_list = []
        return True

    def extract_message(self, message) -> None:
        """Reads a message from the stream and prints the raw output if it is a post"""

        commit = parse_subscribe_repos_message(message)

        if not isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            return

        car = CAR.from_bytes(commit.blocks)

        for op in commit.ops:
            if op.action == "create" and op.cid:
                print("Compiling posts...", end="\r")
                raw_message = car.blocks.get(op.cid)
                if not raw_message:
                    continue
                if raw_message.get("$type") == "app.bsky.feed.post" \
                    and raw_message.get("langs") \
                        and "en" in raw_message.get("langs"):
                    self.message_handling(Message(raw_message))

    def start(self) -> None:
        """Starts the firehose stream"""
        logging.info("Starting firehose stream")
        self.client.start(self.extract_message)


if __name__ == "__main__":
    firehose = BlueSkyFirehose()
    firehose.start()
