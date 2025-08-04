###
# Create Email func
# send email func
# iterate through

from os import environ
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()


class Sender():

    def __init__(self):
        self.ses_client = self.get_ses_client()

    def create_email_from_dict(self, subscription_dict: dict) -> str:
        '''
        Creates HTML to be sent in email
        '''

        subject = f"Activity Spike relating to {subscription_dict['topic_name']}"

        body_text = f"Over the last ten minutes, there have been over {subscription_dict['threshold']} mentions of {subscription_dict['topic_name']}"
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
        AWS_REGION = environ["AWS_DEFAULT_REGION"]
        AWS_ACCESS_KEY_ID = environ["AWS_ACCESS_KEY_ID"]
        AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']

        ses_client = boto3.client(
            "ses",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        return ses_client

    def send_email(self, subscription_dict: dict, email_dict: dict) -> None:
        '''
        Sends a notification email 
        '''
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
        print(response)

    def send_all_emails(self, subs_list: list[dict], ses_client):
        for subscription in subs_list:
            email_dict = self.create_email_from_dict(subscription)
            self.send_email(subscription, email_dict, ses_client)
