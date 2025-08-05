'''
Script to be given to lambda function
'''

from threshold_check import DataGetter, ThresholdChecker
from threshold_ses import Sender
from bot import BlueskyPoster


def lambda_handler(event=None, context=None):
    '''
    Runs the entire email notification mechanism
    '''
    dgetter = DataGetter()

    tchecker = ThresholdChecker()

    subs = tchecker.check_all_thresholds(
        dgetter.subscriptions_dict, dgetter.mentions_df)

    sender = Sender()

    sender.send_all_emails(subs)

    poster = BlueskyPoster()

    poster.post_updates()


lambda_handler()
