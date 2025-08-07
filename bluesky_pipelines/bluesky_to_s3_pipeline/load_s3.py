"""Script to upload Message objects to the S3 bucket."""
import os
import json
from datetime import datetime
import time
import uuid
import logging
import boto3
from dotenv import load_dotenv
from utilities import Message


logging.basicConfig(
    filename="pipeline.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

BUCKET_NAME = 'c18-trend-getter-s3'
FILE_PATH = 'bluesky/raw_posts/'


class S3Loader:
    """Static methods used to load a Message object to the S3"""
    @staticmethod
    def random_string() -> str:
        """Generates a universally unique identifier (UUID) for use as a unique filename."""
        return uuid.uuid4().hex

    @staticmethod
    def format_date(date: datetime) -> str:
        """Formats the timestamp in a filename-appropriate way."""
        return date.strftime("%d-%m-%YT%H-%M-%S")

    @staticmethod
    def load_to_s3(data: list[dict]):
        """Uploads message object to the S3 as a JSON."""
        time1 = time.time()
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "eu-west-2")
        )

        client = session.client("s3")

        filename = f"{S3Loader.random_string()}--{S3Loader.format_date(datetime.now())}.json"

        client.put_object(
            Bucket=BUCKET_NAME,
            Key=f'{FILE_PATH}{filename}',
            Body=json.dumps(data),
            ContentType='application/json'
        )

        time2 = time.time()
        logging.info(
            "%s uploaded to %s in %s seconds", filename, BUCKET_NAME, round(time2-time1, 2))

        return filename

    @staticmethod
    def download_json(data: list[dict]):
        """
        [FOR TESTING PURPOSES]
        Downloads json in the format it would be uploaded to the S3.
        """
        filename = f"{S3Loader.random_string()}--{S3Loader.format_date(datetime.now())}.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        logging.info("%s saved", filename)


if __name__ == "__main__":
    message = Message({
        'text': 'I love donald trump and cooking and photography',
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
    S3Loader.load_to_s3(message)
