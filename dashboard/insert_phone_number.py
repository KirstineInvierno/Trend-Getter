"""This script inserts a phone number into the RDS if it does not already exist"""
import logging
from insert_topic import Connection


logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)


class PhoneNumberInserter():
    """Class for inserting phone number into the users table """

    def __init__(self) -> None:
        """Initialises connection to the database"""
        self.db = Connection()

    def get_user_id(self, phone_number: str) -> int:
        """Retrieve user id when given phone number"""
        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(("""SELECT user_id from bluesky.users
                               WHERE phone_number = %s;"""), (phone_number,))
                    user_id = cur.fetchone()
                    if user_id:
                        return user_id[0]
                    else:
                        return -1
        except Exception as e:
            logging.error("Phone number search failed: %s", e)
            raise
        finally:
            conn.close()

    def insert_number(self, phone_number: str) -> int:
        """Inserts a phone number into the database and returns the user id.
          If the phone number already exists, the user id of the existing user will be returned"""

        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(("""SELECT user_id from bluesky.users
                               WHERE phone_number = %s;"""), (phone_number,))
                    user_id = cur.fetchone()
                    if user_id:
                        return user_id[0]
                    cur.execute(("""INSERT INTO bluesky.users (phone_number)
                               VALUES (%s)
                               RETURNING user_id;"""), (phone_number,))
                    user_id = cur.fetchone()
                    return user_id[0]

        except Exception as e:
            logging.error("Insert failed: %s", e)
            raise
        finally:
            conn.close()
