from os import environ
import datetime
import boto3
import json
from dotenv import load_dotenv
import time


load_dotenv()


def get_s3_connection():
    s3 = boto3.client('s3',
                      aws_access_key_id=environ['AWS_ACCESS_KEY_ID'],
                      aws_secret_access_key=environ['AWS_SECRET_ACCESS_KEY'])
    return s3


def get_5_minutes_ago_seconds():
    now = int(datetime.datetime.now().strftime('%s'))
    five_ago = now - 300
    return five_ago


def get_last_modified(obj):

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


if __name__ == "__main__":
    s3 = get_s3_connection()
    file_list = get_recent_file_names(s3, 'c18-trend-getter-s3')
    print(len(file_list))
    recent_files = get_files_from_last_five_mins(
        file_list, get_5_minutes_ago_seconds())
    print(get_5_minutes_ago_seconds())
    print(recent_files)

    t1 = time.time()
    list_of_jsons = get_json_list(recent_files, s3, 'c18-trend-getter-s3')

    t2 = time.time()
    print(t2-t1)
