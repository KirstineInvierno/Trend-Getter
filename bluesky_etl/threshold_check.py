# get subs
# get latest df
# iterate through subs
# check df.sum
# if it hits, return topic, user_id

from datetime import datetime, timedelta
import boto3
import pandas as pd
import json
from load import DBLoader


def get_subscriptions_data(loader: DBLoader) -> dict:
    '''
    Obtains the current notification subscriptions from RDS
    '''
    conn = loader.get_sql_conn()
    subs_df = pd.read_sql('''SELECT user_id, topic_id, threshold FROM bluesky.user_topic''',
                          con=conn)

    subs_dict = subs_df.to_dict('index')
    return subs_dict


def get_now() -> datetime:
    '''
    Returns the datetime object for now
    '''
    return datetime.now()


def get_ten_minutes_ago(now: datetime) -> str:
    '''
    Returns a string of timestamp ten minutes ago for use in the sql query
    '''
    ten_ago = now - timedelta(minutes=10)
    ten_ago_string = ten_ago.strftime("%Y-%m-%d %H:%M:%S")
    return ten_ago_string


def get_recent_mentions(loader: DBLoader, time_str: str) -> pd.DataFrame:
    '''
    Gets mentions from previous ten minute cycle from RDS
    '''
    conn = loader.get_sql_conn()
    subs_df = pd.read_sql(f"""SELECT mention_id, topic_id FROM bluesky.mention WHERE timestamp > '{time_str}'""",
                          con=conn)
    return subs_df


def check_threshold(threshold_dict: dict, mentions_df: pd.DataFrame) -> bool:
    '''
    Returns true if threshold is met, false otherwise
    '''
    filtered_df = mentions_df[mentions_df['topic_id']
                              == threshold_dict['topic_id']]
    mentions_count = len(filtered_df)
    if mentions_count > threshold_dict['threshold']:
        return True
    return False


def check_all_thresholds(subscriptions_dict: dict, mentions_df: pd.DataFrame):
    '''
    Returns a list of threshold dictionaries which have been met
    '''
    thresholds_met = []
    for row in subscriptions_dict.keys():
        if check_threshold(subscriptions_dict[row], mentions_df):
            thresholds_met.append(subscriptions_dict[row])
    return thresholds_met


if __name__ == '__main__':
    loader = DBLoader()
    sdict = get_subscriptions_data(loader)
    now = get_now()
    weeks_ago = now - timedelta(weeks=10)
    weeks_ago = weeks_ago.strftime("%Y-%m-%d %H:%M:%S")
    tma = get_ten_minutes_ago(now)
    mdf = get_recent_mentions(loader, weeks_ago)
    print(check_all_thresholds(sdict, mdf))
    client = boto3.client('sns')
    response = client.publish(PhoneNumber='+447512843683',
                              Message=json.dumps({'event': 'text', 'msg': 'hello'}))
