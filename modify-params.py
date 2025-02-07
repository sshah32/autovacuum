
# modify-params.py : This script is to modify the db params and reload config. For persistance - I'd modify the postgresql.conf file for changes to take effect next time the change comes in
import psycopg2
import time
from multiprocessing import Process

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "test123",
    "host": "localhost",
    "port": "5432"
}

def modify_database():
    """Creates schema and populates initial data."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    cur.execute("""
    ALTER TABLE test_table SET (
        autovacuum_vacuum_scale_factor = 0.01,
        autovacuum_analyze_scale_factor = 0.01,
        autovacuum_vacuum_cost_delay = 0,
        autovacuum_vacuum_cost_limit = 2000
    )""")
    
    cur.execute("""
    select pg_reload_conf();
    """)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
   modify_database()
