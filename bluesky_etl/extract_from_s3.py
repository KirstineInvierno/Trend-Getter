from os import environ
import datetime
import boto3
import json
from dotenv import load_dotenv
import time
import pandas as pd
from transform_oop import Message, MessageTransformer
from load import DBLoader

load_dotenv()


def get_s3_connection():
    s3 = boto3.client('s3',
                      aws_access_key_id=environ['AWS_ACCESS_KEY_ID'],
                      aws_secret_access_key=environ['AWS_SECRET_ACCESS_KEY'])
    return s3


def get_5_minutes_ago_seconds():
    '''
    Gets time 5 minutes ago
    '''
    now = int(datetime.datetime.now().strftime('%s'))
    five_ago = now - 300
    return five_ago


def get_last_modified(obj):
    '''
    Gets second of last modified (which will be upload)
    '''
    return int(obj['LastModified'].strftime('%s'))


def get_recent_file_names(s3_connection, bucket: str):
    '''
    Returns files sorted by creation time
    '''
    s3_connection = boto3.client('s3')
    objs = s3_connection.list_objects_v2(Bucket=bucket)['Contents']
    sorted_objs = [{'key': obj['Key'], 'last_mod': get_last_modified(
        obj)} for obj in sorted(objs, key=get_last_modified)]
    return sorted_objs


def get_files_from_last_five_mins(sorted_list: list[dict], five_mins_ago: int) -> list[dict]:
    '''
    Returns list of file keys from last 5 mins
    '''
    keys_list = []
    for obj in sorted_list:
        if obj['last_mod'] < 1:
            break
        keys_list.append(obj['key'])
    return keys_list


def get_json_list(recent_file_keys: list[str], s3_connection, bucket: str) -> list[dict]:
    '''
    Returns a list of dictionaries of the json data from last 5 mins
    '''
    json_list = []
    for key in recent_file_keys:
        obj = s3_connection.get_object(Bucket=bucket, Key=key)
        msg_dict = json.loads(obj['Body'].read().decode())
        json_list.append(msg_dict)
    return json_list


def get_topics_dict_from_rds(loader: DBLoader):
    '''
    Obtains a dictionary of current topics from the RDS
    '''
    conn = loader.get_sql_conn()
    topics_df = pd.read_sql('''SELECT topic_name, topic_id FROM bluesky.topic''',
                            con=conn)
    topics_dict = dict(topics_df.values)
    return topics_dict


def get_file_names_to_be_extracted():
    file_list = get_recent_file_names(s3, 'c18-trend-getter-s3')

    recent_files = get_files_from_last_five_mins(
        file_list, get_5_minutes_ago_seconds())
    return recent_files


def transform_messages_into_dataframe(list_of_jsons: list[dict], transformer: MessageTransformer):
    '''
    Uses transform script on every json dictionary and puts it into a dataframe ready to be loaded to the RDS
    '''
    transformed_list = []
    for item in list_of_jsons:
        message = Message(item)
        transformed = transformer.transform(message)
        if transformed is not None:
            transformed_list.append(transformed)


if __name__ == "__main__":
    loader = DBLoader()

    topics_dict = get_topics_dict_from_rds(loader)

    s3 = get_s3_connection()
    file_list = get_recent_file_names(s3, 'c18-trend-getter-s3')

    recent_files = get_files_from_last_five_mins(
        file_list, get_5_minutes_ago_seconds())

    t1 = time.time()
    list_of_jsons = get_json_list(recent_files, s3, 'c18-trend-getter-s3')
    transformer = MessageTransformer(topics_dict)
    transformed_list = []
    t2 = time.time()
    for item in list_of_jsons:
        message = Message(item)
        transformed = transformer.transform(message)
        if transformed is not None:
            transformed_list.append(transformed)
    df = pd.concat(transformed_list)

    t3 = time.time()
    print(
        f'Files imported: {len(file_list)}, {t2-t1} seconds, messages transformed: {len(transformed_list)}, {t3-t2} seconds, total: {t3-t1} seconds')
    print(df)
