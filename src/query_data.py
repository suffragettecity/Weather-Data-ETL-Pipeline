import os
import logging
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
load_dotenv()

db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(db_url)

def run_queries():
    # Querying for business-ready data (Gold Layer)
    logging.info("Connecting to database to run queries:")

    q1 = "SELECT timestamp, temperature_c, humidity_pct FROM silver_weather_forecast LIMIT 5;"
    df_preview = pd.read_sql_query(q1, engine)
    print("--- Data Preview (Silver Layer) ---")
    print(df_preview)
    print("\n" + "="*50 + "\n")

    q2 = """
        SELECT 
            DATE(timestamp) as forecast_date,
            ROUND(AVG(temperature_c)::numeric, 2) as avg_temp_c,
            MAX(temperature_c) as max_temp_c,
            MIN(temperature_c) as min_temp_c,
            ROUND(AVG(humidity_pct)::numeric, 2) as avg_humidity_pct
        FROM silver_weather_forecast
        GROUP BY DATE(timestamp)
        ORDER BY forecast_date;
    """
    df_gold = pd.read_sql_query(q2, engine)
    print("---Daily Weather Metrics (Gold Layer)---")
    print(df_gold)


if __name__ == "__main__":
    try:
        run_queries()
    except Exception as e:
        logging.error(f"Failed to query database: {e}")
