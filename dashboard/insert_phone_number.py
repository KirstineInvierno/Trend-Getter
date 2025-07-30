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

    def insert_number(self, phone_number: str) -> bool:
        """Returns False if phone number already exists. 
        Otherwise, inserts the phone number into the RDS and returns True"""

        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(("""SELECT * from bluesky.users 
                                WHERE phone_number = %s;"""), (phone_number,))
                    if cur.fetchone():
                        return False
                    cur.execute(("""INSERT INTO bluesky.users (phone_number)
                                VALUES (%s);"""), (phone_number,))
                    return True
        except Exception as e:
            logging.error("Insert failed: %s", e)
            raise
        finally:
            conn.close()
