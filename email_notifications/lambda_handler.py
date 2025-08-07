"""Script to be given to lambda function"""
from os import environ
import psycopg2
from dotenv import load_dotenv
from threshold_check import DataGetter, ThresholdChecker
from threshold_ses import Sender


def lambda_handler(event=None, context=None):
    """Runs the entire email notification mechanism"""
    load_dotenv()
    dgetter = DataGetter()

    tchecker = ThresholdChecker()

    subs = tchecker.check_all_thresholds(
        dgetter.subscriptions_dict, dgetter.mentions_df)

    print(dgetter.mentions_df.info())

    sender = Sender()

    sender.send_all_emails(subs)
