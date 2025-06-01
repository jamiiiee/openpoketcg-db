import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    try:
        connection = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
        )
        print("Connection successful!")

        cursor = connection.cursor()

        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print("Current Time:", result)
        print(result)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error connecting to the database: {e}")


get_db_connection()
