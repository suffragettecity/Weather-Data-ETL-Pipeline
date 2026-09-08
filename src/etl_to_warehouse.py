import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import logging
import os
from sqlalchemy import create_engine
import pandas as pd
from google.cloud import bigquery


script_dir = Path(__file__).resolve().parent
env_path = script_dir.parent / ".env"

load_dotenv(dotenv_path=env_path)


def extract_from_db():
    logging.info("Extracting data from PostgreSQL database...")

    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)
    to_bq_df = pd.read_sql("SELECT * FROM silver_weather_forecast", engine)
    return to_bq_df


def load_to_bigquery(to_bq_df):
    project_id = os.getenv("BIGQUERY_PROJECT_ID")
    dataset = os.getenv("BIGQUERY_DATASET")
    table = os.getenv("BIGQUERY_TABLE")
    table_id = f"{project_id}.{dataset}.{table}"

    client = bigquery.Client(project=project_id)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")

    job = client.load_table_from_dataframe(to_bq_df, table_id, job_config=job_config)
    job.result() # wait for completion
    print(f"Loaded {job.output_rows} rows into {table_id}")


if __name__ == "__main__":
    df = extract_from_db()
    load_to_bigquery(df)
