import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import pandas as pd
import requests
from sqlalchemy import create_engine
from pathlib import Path

script_dir = Path(__file__).resolve().parent
env_path = script_dir.parent / ".env"  # Assumes .env is in the root

load_dotenv(dotenv_path=env_path)


def extract_weather_data():
    logging.info("Starting data extraction...")

    base_url = os.getenv("OPENWEATHER_API_URL")
    api_key = os.getenv("OPENWEATHER_API_KEY")

    # temporary force check
    print(f"\n[DEBUG] URL is: {base_url}")

    params = {
        "lat": -12.05,       # latitude and longitude for Lima, Peru
        "lon": -77.04,
        "appid": api_key,
        "units": "metric",
    }

    response = requests.get(base_url + "forecast", params=params, timeout=10)

    return response.json()


def transform_weather_data(raw_data):
    logging.info("Transforming raw data...")
    try:
        hourly_data = raw_data["list"]
        cleaned_rows = []

        for block in hourly_data:
            row = {
                "timestamp": block["dt_txt"],
                "temperature_c": block["main"]['temp'],
                "humidity_pct": block["main"]["humidity"],
                "weather_main": block["weather"][0]["main"],
                "weather_description": block["weather"][0]["description"],
                "extracted_at": datetime.now(),
            }
            cleaned_rows.append(row)

        df = pd.DataFrame(cleaned_rows)

        df["timestamp"] = pd.to_datetime(df['timestamp'])
        df.dropna(subset=["timestamp", "temperature_c"])

        logging.info("Transformation successful")
        return df

    except KeyError as e:
        logging.error(f"Transformation failed: {e}")
        raise


def load_to_postgres(df):
    logging.info("Streaming data load to postgresql...")

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
        df.to_sql("silver_weather_forecast", engine, if_exists="append", index=False)
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

