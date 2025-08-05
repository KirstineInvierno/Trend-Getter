'''Script sends email notifications to email list'''
from os import environ
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from email_notifications.threshold_check import DataGetter, ThresholdChecker


load_dotenv()


class Sender():
    '''
    Class which sends emails
    '''

    def __init__(self):
        '''
        Initializes instances with ses client
        '''
        self.ses_client = self.get_ses_client()

    def create_email_from_dict(self, subscription_dict: dict) -> str:
        '''
        Creates HTML to be sent in email
        '''

        subject = f"Activity Spike relating to {subscription_dict['topic_name']}"

        body_text = ("Over the last ten minutes, there have been over"
                     f"{subscription_dict['threshold']} "
                     f"mentions of {subscription_dict['topic_name']}."
                     f"In total, there were {subscription_dict['mention_count']}.")

        body_html = f"""<html>
        <head></head>
        <body>
            <h1>{subject}</h1>
            <p>{body_text}</p>
        </body>
        </html>"""
        email_dict = {'subject': subject, 'text': body_text, 'html': body_html}
        return email_dict

    def get_ses_client(self):
        '''
        Returns a ses client to use to send emails
        '''
        region = environ["AWS_DEFAULT_REGION"]
        access_key = environ["AWS_ACCESS_KEY_ID"]
        secret_key = environ['AWS_SECRET_ACCESS_KEY']

        ses_client = boto3.client(
            "ses",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        return ses_client

    def send_email(self, subscription_dict: dict, email_dict: dict) -> None:
        '''
        Sends a notification email 
        '''
        print('sending')
        try:
            response = self.ses_client.send_email(
                Source=environ['SENDER_EMAIL'],
                Destination={
                    'ToAddresses': [
                        subscription_dict['email'],
                    ],
                },
                Message={
                    'Subject': {
                        'Data': email_dict['subject']
                    },
                    'Body': {
                        'Text': {
                            'Data': email_dict['text']
                        },
                        'Html': {
                            'Data': email_dict['html']
                        }
                    }
                }
            )
            print(response, 'sent')
        except ClientError:
            print(f'{subscription_dict['email']} not verified')

    def send_all_emails(self, subs_list: list[dict]):
        '''
        Calls send_email function for each notification required
        '''
        for subscription in subs_list:
            email_dict = self.create_email_from_dict(subscription)
            self.send_email(subscription, email_dict)


if __name__ == "__main__":
    dgetter = DataGetter()
    print(dgetter.subscriptions_dict)
    tchecker = ThresholdChecker()

    subs = tchecker.check_all_thresholds(
        dgetter.subscriptions_dict, dgetter.mentions_df)

    print(subs)

    sender = Sender()
    sender.send_all_emails(subs)
