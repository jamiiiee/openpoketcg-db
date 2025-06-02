import psycopg2
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


@contextmanager
def db_cursor():
    try:
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
        )
    except Exception as e:
        raise RuntimeError(f"Failed to connect to the database: {e}") from e

    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
