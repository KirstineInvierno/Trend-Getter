"""Script to load a prepared message dataframe into the RDS database."""

from os import environ
import pandas as pd
import sqlalchemy
import psycopg2
import logging
from dotenv import load_dotenv
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)

class DBLoader():
    """Handles upload of data to RDS."""

    def get_sql_conn(self):
        """Returns connection to RDS."""
        try:
            host = environ["DB_HOST"]
            user = environ["DB_USER"]
            password = environ["DB_PASSWORD"]
            database = environ["DB_NAME"]
            engine = sqlalchemy.create_engine(
                f"postgresql+psycopg2://{user}:{password}@{host}/{database}")
            logging.info("Successfully connected to the RDS.")
            return engine
        except SQLAlchemyError as e:
            logging.error("Failed to connect to RDS. Error: %s", e)
            raise

    def upload_df_to_mention(self, df: pd.DataFrame,
                             engine: Engine, schema: str) -> None:
        """Uploads data to the RDS."""
        with engine.begin() as conn:
            df.to_sql(
                'mention',
                con=conn,
                if_exists="append",
                index=False,
                schema=schema
            )
            logging.info("Uploaded %s rows to the RDS.", len(df))


if __name__ == "__main__":
    loader = DBLoader()
    df = pd.DataFrame()
    con = loader.get_sql_conn()
    loader.upload_df_to_mention(engine=con, df=df, schema="bluesky")
