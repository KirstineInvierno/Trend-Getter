'''
This script loads a prepared message dataframe into the RDS database 
'''

from os import environ
import pandas as pd
import sqlalchemy
import psycopg2
from dotenv import load_dotenv
from extract import BlueSkyFirehose


load_dotenv()


class DBLoader():
    '''
    Class which deals with the upload of the data
    '''

    def get_sql_conn(self):
        '''
        Returns connection to RDS
        '''
        host = environ["DB_HOST"],
        user = environ["DB_USER"],
        password = environ["DB_PASSWORD"],
        database = environ["DB_NAME"],
        engine = sqlalchemy.create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}/{database}")
        return engine

    def upload_df_to_mention(self, df: pd.DataFrame, engine: sqlalchemy.engine, schema: str) -> None:
        '''
        Performs the upload to the RDS
        '''
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
    con = loader.get_sql_conn()
    loader.upload_df_to_mention()
