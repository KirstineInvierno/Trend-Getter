# pylint: disable=R0903
"""Script to connect to AWS S3, extract the latest uploaded JSON file,
and convert it into a pandas DataFrame for transformation."""

from os import environ
import json
import logging
import boto3
from dotenv import load_dotenv
import pandas as pd
from transform import Message, MessageTransformer
from load import DBLoader

logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)

BUCKET = "c18-trend-getter-s3"
PREFIX = "bluesky/raw_posts/"


class S3Connection():
    """Handles loading environment variables and establishes a connection to the S3 bucket."""

    def __init__(self) -> None:
        load_dotenv()
        try:
            self.s3 = boto3.client(
            "s3",
            aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"]
        )
            logging.info("Successfully connected to AWS S3.")
        except ConnectionError as e:
            logging.error("Unable to connect to AWS S3. Error: %s", e)
            self.s3 = None

    def get_s3_connection(self) -> boto3.client:
        """Returns the boto3 S3 client."""
        return self.s3


class DatabaseTopicExtractor:
    """Connects to the RDS to obtain a dictionary of topics."""

    def get_topics_dict_from_rds(self, loader: DBLoader)-> dict[str, str]:
        """Obtains a dictionary of current topics from the RDS."""
        try:
            conn = loader.get_sql_conn()
            logging.info("Successfully connected to RDS.")

            topics_df = pd.read_sql("""SELECT topic_name, topic_id FROM bluesky.topic""",
                                    con=conn)
            topics_dict = dict(topics_df.values)
            logging.info("Retrieved %s topics from RDS.", len(topics_dict))
            return topics_dict

        except ConnectionError as e:
            logging.error("Unable to connect to RDS. Error: %s", e)
            return {}


class S3FileExtractor():
    """Extracts metadata and file content from an S3 bucket."""

    def __init__(self, connection) -> None:
        self.s3 = connection

    def get_latest_file_key(self, bucket: str) -> str:
        """Returns the key of the most recently uploaded file in the bucket."""
        logging.info("Fetching latest file from S3.")
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=PREFIX)
        objects = response.get("Contents")

        if not objects:
            logging.error("No files found in S3 bucket.")
            raise FileNotFoundError("No files found in S3 bucket.")

        latest_object = max(objects, key=lambda x: x["LastModified"])
        return latest_object["Key"]


class Converter():
    """Class to convert extracted S3 file into a pandas Dataframe."""

    def __init__(self, s3_extractor):
        self.s3_extractor = s3_extractor
        self.s3 = s3_extractor.s3

    def get_latest_file_as_dicts(self, bucket: str) -> list[dict]:
        """Downloads the latest file from the S3 bucket and returns a list of python dicts."""
        key = self.s3_extractor.get_latest_file_key(bucket)
        logging.info("Downloading file: %s", key)
        response = self.s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
        logging.info("JSON file successfully converted.")

        return json.loads(content)

    @staticmethod
    def transform_messages_into_dataframe(list_of_jsons: list[dict],
                                          transformer: MessageTransformer) -> pd.DataFrame:
        """Uses transform script on every json dictionary 
        and puts it into a dataframe ready to be loaded to the RDS."""
        transformed_list = []
        for item in list_of_jsons:
            message = Message(item)
            transformed = transformer.transform(message)
            if transformed is not None:
                transformed_list.append(transformed)
        df = pd.concat(transformed_list)
        return df


if __name__ == "__main__":
    connection = S3Connection()
    conn = connection.get_s3_connection()

    loader = DBLoader()
    topic_extractor = DatabaseTopicExtractor()
    topics_dict = topic_extractor.get_topics_dict_from_rds(loader)

    s3_extractor = S3FileExtractor(conn)
    converter = Converter(s3_extractor)
    transformer = MessageTransformer(topics_dict=topics_dict)

    messages_dict_list = converter.get_latest_file_as_dicts(BUCKET)

    df = converter.transform_messages_into_dataframe(messages_dict_list, transformer)

    if df is not None and not df.empty:
        engine = loader.get_sql_conn()
        logging.info("Uploading DataFrame to database...")
        loader.upload_df_to_mention(df=df, engine=engine, schema="bluesky")
        logging.info("Upload complete.")
    else:
        logging.warning("No data to upload.")
