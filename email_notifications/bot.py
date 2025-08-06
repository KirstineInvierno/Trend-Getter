from os import environ
from atproto import Client
from dotenv import load_dotenv
from threshold_check import DataGetter

load_dotenv()


class BlueskyPoster:
    """Posts about bluesky mentions"""

    def __init__(self, email=environ["BLUESKY_EMAIL"], password=environ["BLUESKY_PASSWORD"]):
        self._email = email
        self._password = password
        self.client = Client()
        self.client.login(self._email, self._password)

    def post(self, text: str):
        """posts a message from the bot"""
        return self.client.send_post(text)

    def post_updates(self):
        """Posts all updates on last ten minutes"""
        dg = DataGetter()
        for topic in dg.topics_dict.keys():
            text = f"There have been {dg.topics_dict[topic]} mentions of {topic} in the last 10 minutes."
            self.post(text=text)
