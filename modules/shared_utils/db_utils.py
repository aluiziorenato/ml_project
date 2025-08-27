import os
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432")
    )
    return conn

def execute_query(query, params=None):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        result = cur.fetchall()
    conn.close()
    return result
