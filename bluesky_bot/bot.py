import os
from atproto import Client
from dotenv import load_dotenv

load_dotenv()


class BlueskyPoster:
    def __init__(self, email=os.getenv("BLUESKY_EMAIL"), password=os.getenv("BLUESKY_PASSWORD")):
        self._email = email
        self._password = password
        self.client = Client()
        self.client.login(self._email, self._password)

    def post(self, text: str):
        return self.client.send_post(text)


def main():
    poster = BlueskyPoster()
    poster.post("we're so trendy")


if __name__ == "__main__":
    main()
