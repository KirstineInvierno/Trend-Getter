"""Script to load a prepared message dataframe into the RDS database."""

from os import environ
import time
import pandas as pd
import sqlalchemy
import psycopg2
from dotenv import load_dotenv
import logging


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class DBLoader():
    """Class to handle uploading data."""

    def get_sql_conn(self):
        """Returns connection to the RDS."""
        host=environ["DB_HOST"]
        user=environ["DB_USER"]
        password=environ["DB_PASSWORD"]
        database=environ["DB_NAME"]
        engine=sqlalchemy.create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}/{database}")
        return engine

    def upload_df_to_mention(self, df: pd.DataFrame,
                             engine: sqlalchemy.engine, schema: str) -> None:
        """Handles upload to the RDS."""
        with engine.begin() as conn:
            df.to_sql(
                'mention',
                con=conn,
                if_exists="append",
                index=False,
                schema=schema
            )
            conn.commit()


if __name__ == '__main__':
    loader = DBLoader()
    df = pd.DataFrame()
    time1 = time.time()
    logging.info('Connecting...')
    con = loader.get_sql_conn()
    time2 = time.time()
    logging.info(f'Connected in {round(time2-time1, 2)} seconds')
    logging.info('Uploading...')
    loader.upload_df_to_mention(engine=con, df=df, schema='bluesky')
    time3 = time.time()
    logging.info(f'Uploaded in {round(time3-time2, 2)} seconds')
    logging.info(
        f'Load completed in a total of {round(time3-time1, 2)} seconds')
