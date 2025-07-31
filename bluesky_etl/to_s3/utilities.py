import json
from datetime import datetime


class MessageError(Exception):
    """Error for when creating Message object"""


class Message:
    """message recieved from API"""

    def __init__(self, message_dict: dict):
        self._validation(message_dict)

        self.text = message_dict.get("text")
        self.langs = message_dict.get("langs")
        self.type = message_dict.get("$type")
        self._timestamp = None
        self._timestamp_string = message_dict.get("createdAt")
        self._json_string = None

    def _validation(self, message_dict: dict):
        required_fields = [
            "text",
            "langs",
            "$type",
            "createdAt"
        ]

        for field in required_fields:
            if field not in message_dict:
                raise MessageError(
                    f"Your message is missing the required field: {field} ")

    @property
    def timestamp(self) -> datetime:
        """Extracts timestamp from message"""
        if self._timestamp is None:
            temp_timestamp = self._timestamp_string
            self._timestamp = datetime.fromisoformat(temp_timestamp)

        return self._timestamp

    @property
    def json_string(self) -> str:
        if self._json_string is None:
            json_dict = {
                "text": self.text,
                "langs": self.langs,
                "$type": self.type,
                "createdAt": self._timestamp_string
            }
            self._json_string = json.dumps(json_dict)

        return self._json_string
