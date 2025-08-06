'''Script to obtain data from RDS to check whether users need to be notified.'''
from os import environ
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
import sqlalchemy


class DataGetter():

    """Class which interacts with db"""

    def __init__(self):
        """Initializes DataGetter"""
        load_dotenv()
        self.sql_conn = self.get_sql_conn()
        self.subscriptions_dict = self.get_subscriptions_data()
        self.mentions_df = self.get_recent_mentions()
        self.topics_dict = self.get_topics_dict(5)

    def get_subscriptions_data(self) -> dict:
        """Obtains the current notification subscriptions from RDS"""
        subs_df = pd.read_sql('''SELECT user_id, email, topic_id,
                                topic_name, threshold
                                FROM bluesky.user_topic
                                    JOIN bluesky.users USING(user_id)
                                    JOIN bluesky.topic USING(topic_id)''',
                              con=self.sql_conn)

        subs_dict = subs_df.to_dict('index')
        return subs_dict

    def get_sql_conn(self):
        """Returns connection to RDS"""
        host = environ["DB_HOST"]
        user = environ["DB_USER"]
        password = environ["DB_PASSWORD"]
        database = environ["DB_NAME"]
        engine = sqlalchemy.create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}/{database}")
        return engine

    def get_now(self) -> datetime:
        """Returns the datetime object for now"""
        return datetime.now()

    def get_ten_minutes_ago(self) -> str:
        """Returns a string of timestamp ten minutes ago for use in the sql query"""
        now = self.get_now()
        ten_ago = now - timedelta(days=10)
        ten_ago_string = ten_ago.strftime("%Y-%m-%d %H:%M:%S")
        return ten_ago_string

    def get_recent_mentions(self) -> pd.DataFrame:
        """Gets mentions from previous ten minute cycle from RDS"""
        time_str = self.get_ten_minutes_ago()
        mentions_df = pd.read_sql(f"""SELECT mention_id, topic_id, topic_name
                                  FROM bluesky.mention 
                                    JOIN bluesky.topic USING (topic_id) WHERE timestamp > '{time_str}'""",
                                  con=self.sql_conn)
        return mentions_df

    def get_topics_dict(self, threshold: int) -> dict:
        """Returns list of topics with over a threshold of mentions"""
        mentions_vc = dict(self.mentions_df['topic_name'].value_counts(
        ).loc[lambda x: x > threshold])
        return mentions_vc


class ThresholdChecker():
    """Class which checks whether the mentions threshold has been reached"""

    def check_threshold(self, threshold_dict: dict, mentions_df: pd.DataFrame) -> int | bool:
        """Returns true if threshold is met, false otherwise"""
        filtered_df = mentions_df[mentions_df['topic_id']
                                  == threshold_dict['topic_id']]
        mentions_count = len(filtered_df)
        if mentions_count > threshold_dict['threshold']:
            return mentions_count
        return False

    def check_all_thresholds(self, subscriptions_dict: dict, mentions_df: pd.DataFrame):
        """Returns a list of threshold dictionaries which have been met"""

        thresholds_met = []
        for row in subscriptions_dict.keys():
            count = self.check_threshold(subscriptions_dict[row], mentions_df)
            if count:
                subscriptions_dict[row]['mention_count'] = count
                thresholds_met.append(subscriptions_dict[row])
        return thresholds_met
