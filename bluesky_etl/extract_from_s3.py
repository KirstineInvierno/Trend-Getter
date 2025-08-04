"""Script to connect to AWS S3, extract the latest uploaded JSON file,
and convert it into a pandas DataFrame for transformation."""

from os import environ
import boto3
import json
import io
import logging
from dotenv import load_dotenv
import pandas as pd
from transform import Message, MessageTransformer
# from bluesky_etl.transform import Message, MessageTransformer
# from load import DBLoader

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
            's3',
            aws_access_key_id=environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=environ['AWS_SECRET_ACCESS_KEY']
        )
            logging.info("Successfully connected to AWS S3.")
        except Exception as e:
            logging.error(f"Unable to connect to AWS S3. Error: {e}")

    def get_s3_connection(self) -> boto3.client:
        """Returns the boto3 S3 client."""
        return self.s3

class Extractor():
    """Extracts metadata and file content from an S3 bucket."""

    def __init__(self, connection) -> None:
        self.s3 = connection

    def get_latest_file_key(self, bucket: str) -> str:
        """Returns the key of the most recently uploaded file in the bucket."""
        logging.info("Fetching latest key")
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=PREFIX)
        objects = response.get("Contents")

        if not objects:
            logging.error("No files found in S3 bucket.")

        # Sort objects by LastModified descending
        latest_object = max(objects, key=lambda x: x["LastModified"])
        return latest_object["Key"]

    def get_latest_file_as_dicts(self, bucket: str) -> list[dict]:
        """Downloads the latest file from the S3 bucket and returns a list of python dicts."""
        key = self.get_latest_file_key(bucket)
        logging.info(f"Downloading file: {key}")
        response = self.s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
        logging.info("JSON file successfully converted.")

        return json.loads(content)
    
    def return_single_message_as_dict(self, bucket: str):
        """Generator that yields one dict (message) at a time from the latest S3 JSON file."""
        messages = self.get_latest_file_as_dicts(bucket)
        for message_dict in messages:
            yield message_dict


if __name__ == "__main__":
    connection = S3Connection()
    conn = connection.get_s3_connection()
    extractor = Extractor(conn)
    transformer = MessageTransformer

    for message_dict in extractor.return_single_message_as_dict(BUCKET):
        try:
            message = Message(message_dict)
            df = transformer.transform(message)
            if df is not None:
                print(df)
        except ValueError as e:
            logging.warning(f"Skipping invalid message: {e}")

    print("finished")


    # def get_5_minutes_ago_seconds(self):
    #     '''
    #     Gets time in seconds 5 minutes ago
    #     '''
    #     now = int(datetime.datetime.now().strftime('%s'))
    #     five_ago = now - 300
    #     return five_ago


    # def get_last_modified(obj):
    #     '''
    #     Gets second of last modified (which will be upload)
    #     '''
    #     return int(obj['LastModified'].strftime('%s'))


    # def get_recent_file_names(s3_connection, bucket: str):
    #     '''
    #     Returns files sorted by creation time
    #     '''
    #     s3_connection = boto3.client('s3')
    #     objs = s3_connection.list_objects_v2(Bucket=bucket)['Contents']
    #     sorted_objs = [{'key': obj['Key'], 'last_mod': get_last_modified(
    #         obj)} for obj in sorted(objs, key=get_last_modified)]
    #     return sorted_objs


# def get_files_from_last_five_mins(sorted_list: list[dict], five_mins_ago: int) -> list[dict]:
#     '''
#     Returns list of file keys from last 5 mins, loops through list of s3 objects ordered 
#     by recent first and ends loop when it finds one over 5 mins old 
#     '''
#     keys_list = []
#     for obj in sorted_list:
#         if obj['last_mod'] < five_mins_ago:
#             break
#         keys_list.append(obj['key'])
#     return keys_list


# def get_json_list(recent_file_keys: list[str], s3_connection, bucket: str) -> list[dict]:
#     '''
#     Returns a list of dictionaries of the json data from last 5 mins
#     '''
#     json_list = []
#     for key in recent_file_keys:
#         obj = s3_connection.get_object(Bucket=bucket, Key=key)
#         msg_dict = json.loads(obj['Body'].read().decode())
#         json_list.append(msg_dict)
#     return json_list


# def get_topics_dict_from_rds(loader: DBLoader):
#     '''
#     Obtains a dictionary of current topics from the RDS
#     '''
#     conn = loader.get_sql_conn()
#     topics_df = pd.read_sql('''SELECT topic_name, topic_id FROM bluesky.topic''',
#                             con=conn)
#     topics_dict = dict(topics_df.values)
#     return topics_dict


# def get_file_names_to_be_extracted():
#     file_list = get_recent_file_names(s3, 'c18-trend-getter-s3')

#     recent_files = get_files_from_last_five_mins(
#         file_list, get_5_minutes_ago_seconds())
#     return recent_files


# def transform_messages_into_dataframe(list_of_jsons: list[dict], transformer: MessageTransformer):
#     '''
#     Uses transform script on every json dictionary and puts it into a dataframe ready to be loaded to the RDS
#     '''
#     transformed_list = []
#     for item in list_of_jsons:
#         message = Message(item)
#         transformed = transformer.transform(message)
#         if transformed is not None:
#             transformed_list.append(transformed)
#     df = pd.concat(transformed_list)
#     return df


# if __name__ == "__main__":
#     loader = DBLoader()

#     topics_dict = get_topics_dict_from_rds(loader)

#     s3 = get_s3_connection()
#     file_list = get_recent_file_names(s3, 'c18-trend-getter-s3')

#     recent_files = get_files_from_last_five_mins(
#         file_list, get_5_minutes_ago_seconds())

#     t1 = time.time()
#     list_of_jsons = get_json_list(recent_files, s3, 'c18-trend-getter-s3')
#     transformer = MessageTransformer(topics_dict)

#     t2 = time.time()

#     df_for_load = transform_messages_into_dataframe(
#         list_of_jsons=list_of_jsons, transformer=transformer)

#     t3 = time.time()
#     print(
#         f'Files imported: {len(file_list)}, {t2-t1} seconds, messages transformed: {len(df_for_load)}, {t3-t2} seconds, total: {t3-t1} seconds')
#     print(df_for_load)


# latest_key = get_latest_file_key(s3, "your-bucket-name")
# df = get_json_list(s3, "your-bucket-name", [latest_key])
