"""Script to add a subscription into the RDS"""

import logging
from insert_topic import Connection


logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)


class SubscriptionInserter():
    """Subscribes a user to a topic if they are not already subscribied"""

    def __init__(self) -> None:
        self.db = Connection()

    def insert_subscription(self, user_id: int, topic_id: int) -> bool:
        """Inserts a subscription into the database and returns True
           if the subscription is successfully inserted. Returns
           False if the subscription already exists."""
        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT * FROM bluesky.user_topic
                        WHERE user_id = %s AND topic_id = %s;
                    """, (user_id, topic_id))
                    if cur.fetchone():
                        return False

                    cur.execute("""
                        INSERT INTO bluesky.user_topic (user_id, topic_id,active)
                        VALUES (%s, %s,TRUE);
                    """, (user_id, topic_id))
                    return True
        except Exception as e:
            logging.error("Subscription insert failed: %s", e)
            raise
        finally:
            conn.close()
