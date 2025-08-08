"""Script to run the ETL, automatically updating the RDS."""
# pylint: disable=W0613

import logging
from extract_from_s3 import S3Connection, DatabaseTopicExtractor, S3FileExtractor, Converter, BUCKET
from transform import MessageTransformer
from load_to_rds import DBLoader

logging.basicConfig(format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)

def lambda_handler(event=None, context=None) -> dict:
    """AWS Lambda entry point for the ETL."""
    try:
        s3_connection = S3Connection()
        s3_client = s3_connection.get_s3_connection()

        s3_extractor = S3FileExtractor(s3_client)
        converter = Converter(s3_extractor)

        logging.info("Starting extraction process.")
        data_dicts = converter.get_latest_file_as_dicts(BUCKET)

        loader = DBLoader()
        topics_dict = DatabaseTopicExtractor().get_topics_dict_from_rds(loader)
        logging.info("Extraction complete.")


        logging.info("Starting transformation process.")
        transformer = MessageTransformer(topics_dict=topics_dict)
        df = converter.transform_messages_into_dataframe(data_dicts, transformer)
        logging.info("Transformation complete.")

        logging.info("Starting upload process.")
        if df is not None and not df.empty:
            logging.info("Uploading transformed DataFrame to RDS.")
            engine = loader.get_sql_conn()
            loader.upload_df_to_mention(df=df, engine=engine, schema="bluesky")
            logging.info("Upload complete.")
            return {"statusCode": 200, "body": "ETL completed successfully."}
        logging.warning("No data to upload.")
        return {"statusCode": 204, "body": "No data to upload."}

    except Exception as e:
        logging.error("ETL failed: %s", e, exc_info=True)
        return {"statusCode": 500, "body": f"ETL failed: {e}"}
