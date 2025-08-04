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


class DataGetter():

    '''
    Class which interacts with db
    '''

    def __init__(self, loader: DBLoader):
        '''
        Initializes DataGetter
        '''
        self.subscriptions_dict = self.get_subscriptions_data(loader)
        self.mentions_df = self.get_recent_mentions(loader)

    def get_subscriptions_data(self, loader: DBLoader) -> dict:
        '''
        Obtains the current notification subscriptions from RDS
        '''
        conn = loader.get_sql_conn()
        subs_df = pd.read_sql('''SELECT user_id, email, topic_id, topic_name, threshold 
                                FROM bluesky.user_topic 
                                    JOIN bluesky.users USING(user_id)
                                    JOIN bluesky.topic USING(topic_id)''',
                              con=conn)

        subs_dict = subs_df.to_dict('index')
        return subs_dict

    def get_now(self) -> datetime:
        '''
        Returns the datetime object for now
        '''
        return datetime.now()

    def get_ten_minutes_ago(self) -> str:
        '''
        Returns a string of timestamp ten minutes ago for use in the sql query
        '''
        now = self.get_now()
        ten_ago = now - timedelta(minutes=10)
        ten_ago_string = ten_ago.strftime("%Y-%m-%d %H:%M:%S")
        return ten_ago_string

    def get_recent_mentions(self, loader: DBLoader) -> pd.DataFrame:
        '''
        Gets mentions from previous ten minute cycle from RDS
        '''
        time_str = self.get_ten_minutes_ago()
        conn = loader.get_sql_conn()
        mentions_df = pd.read_sql(f"""SELECT mention_id, topic_id FROM bluesky.mention WHERE timestamp > '{time_str}'""",
                                  con=conn)
        return mentions_df


class ThresholdChecker():

    def check_threshold(self, threshold_dict: dict, mentions_df: pd.DataFrame) -> bool:
        '''
        Returns true if threshold is met, false otherwise
        '''
        filtered_df = mentions_df[mentions_df['topic_id']
                                  == threshold_dict['topic_id']]
        mentions_count = len(filtered_df)
        if mentions_count > threshold_dict['threshold']:
            return True
        return False

    def check_all_thresholds(self, subscriptions_dict: dict, mentions_df: pd.DataFrame):
        '''
        Returns a list of threshold dictionaries which have been met
        '''
        thresholds_met = []
        for row in subscriptions_dict.keys():
            if self.check_threshold(subscriptions_dict[row], mentions_df):
                thresholds_met.append(subscriptions_dict[row])
        return thresholds_met


if __name__ == '__main__':
    loader = DBLoader()
    dgetter = DataGetter(loader)
    print(dgetter.subscriptions_dict)
    tchecker = ThresholdChecker()

    print(tchecker.check_all_thresholds(
        dgetter.subscriptions_dict, dgetter.mentions_df))
