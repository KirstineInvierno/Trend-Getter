"""Script to add a subscription into the RDS"""


import logging
from insert_topic import Connection


logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)


class SubscriptionInserter():
    """Subscribes a user to a topic if they are not already subscribed"""

    def __init__(self) -> None:
        self.db = Connection()

    def insert_subscription(self, user_id: int, topic_id: int, threshold: int) -> bool:
        """Inserts a subscription into the database and returns True
           if the subscription is successfully inserted. If the subscription already
           exists, the threshold is updated and returns False."""
        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                       SELECT * FROM bluesky.user_topic
                       WHERE user_id = %s AND topic_id = %s;
                   """, (user_id, topic_id))
                    if cur.fetchone():
                        cur.execute("""UPDATE bluesky.user_topic
                                    SET threshold = %s
                                    WHERE user_id = %s and topic_id = %s;""", (threshold, user_id, topic_id))
                        return False

                    cur.execute("""
                       INSERT INTO bluesky.user_topic (user_id, topic_id,active,threshold)
                       VALUES (%s, %s,TRUE,%s);
                   """, (user_id, topic_id, threshold))
                    return True
        except Exception as e:
            logging.error("Subscription insert failed: %s", e)
            raise
        finally:
            conn.close()

    def get_subscriptions(self, user_id: int) -> list[str]:
        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                       SELECT topic_name
                       FROM bluesky.user_topic
                       JOIN bluesky.topic using(topic_id)
                       WHERE user_id = %s ;
                   """, (user_id,))
                    topics = cur.fetchall()
                    return [topic[0] for topic in topics]

        except Exception as e:
            logging.error("Subscription retrieval failed: %s", e)
            raise
        finally:
            conn.close()

    def unsubscribe(self, user_id: int, topic_name: str) -> bool:
        """deletes subscription for a user if they were subscribed."""
        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                       DELETE FROM bluesky.user_topic
                       USING bluesky.topic
                       WHERE user_topic.user_id = %s
                       AND user_topic.topic_id = topic.topic_id
                       AND topic.topic_name = %s;
                   """, (user_id, topic_name))
                    return cur.rowcount > 0

        except Exception as e:
            logging.error("Unsubscription failed: %s", e)
            raise
        finally:
            conn.close()
