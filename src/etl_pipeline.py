import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import pandas as pd
import requests
from sqlalchemy import create_engine

load_dotenv()


def extract_weather_data():
    logging.info("Starting data extraction...")

    base_url = os.getenv("WEATHER_API_URL")

    try:
        # pass params dictionary directly to requests.get
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        logging.info("Extraction successful")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Extraction failed: {e}")
        raise


def transform_weather_data(raw_data):
    logging.info("Transforming raw data...")
    try:
        hourly_data = raw_data["hourly"]
        df = pd.DataFrame(
            {
                "timestamp": hourly_data["time"],
                "temperature_c": hourly_data["temperature_2m"],
                "humidity_pct": hourly_data["relative_humidity_2m"],
            }
        )
        df["timestamp"] = pd.to_datetime(df['timestamp'])
        df["extracted_at"] = datetime.now()
        df.dropna(subset=["timestamp", "temperature_c"])
        return df
    except KeyError as e:
        logging.error(f"Transformation failed: {e}")
        raise


def load_to_postgres(df):
    logging.info("Starting data load to postgresql...")

    # get database credentials from environment variables
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    # construct the connection string dynamically (runtime)
    db_url = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    try:
        engine = create_engine(db_url)
        df.to_sql("hourly_forecast", engine, if_exists="append", index=False)
        logging.info("Data load to PostgreSQL successful.")
    except Exception as e:
        logging.error(f"PostgreSQL load failed: {e}")
        raise


if __name__ == "__main__":
    try:
        raw_json = extract_weather_data()
        clean_df = transform_weather_data(raw_json)
        load_to_postgres(clean_df)
        logging.info("ETL pipeline completed successfully!")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

