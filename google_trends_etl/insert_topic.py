import psycopg2
from os import environ
from dotenv import load_dotenv
import logging

logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)

class Connection():
    def __init__(self):
        load_dotenv()

    def get_connection(self):
        try:
            logging.info("Connecting to the database.")
            conn = psycopg2.connect(
                host=environ["DB_HOST"],
                user=environ["DB_USER"],
                password=environ["DB_PASSWORD"],
                dbname=environ["DB_NAME"]
            )
            return conn
        except Exception as e:
            logging.error("Database connection failed: %s", e)
            raise

class TopicInserter():
    def __init__(self):
        self.db = Connection()

    def insert_topic(self, topic_name: str):
        topic_name = topic_name.strip().lower()
        if not topic_name:
            raise ValueError("No topic(s) entered.")

        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(("""INSERT INTO bluesky.topic (topic_name)
                                VALUES (%s)
                                ON CONFLICT (topic_name) DO NOTHING;"""), (topic_name,))
                    logging.info("Inserted topic: %s", topic_name)
        except Exception as e:
            logging.error("Insert failed: %s", e)
            raise
        finally:
            conn.close()