import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            port=os.environ.get("DB_PORT", 5432)
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None