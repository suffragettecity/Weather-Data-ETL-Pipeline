import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine

# setup logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s -%(message)s")


load_dotenv()


def test_database_connection():
    logging.info("Attempting to connect to PostgreSQL container...")

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    try:
        # Create connection engine and attempt to connect
        engine = create_engine(db_url)
        with engine.connect() as connection:
            logging.info("Python successfully established a connection to the dockerized PostgreSQL DB")

    except Exception as e:
        logging.error("Connection failed :(")
        logging.error(f"Error details: {e}")


if __name__ == "__main__":
    test_database_connection()
