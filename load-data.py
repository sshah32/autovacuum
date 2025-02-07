# load-data.py: This script is to help load initial schema,mock data and monitor-autovacuum function
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

def setup_database():
    """Creates schema and populates initial data."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dba_sanchit.test2 (
        id SERIAL PRIMARY KEY,
        name varchar(255),
        address text,
        created_at TIMESTAMP DEFAULT NOW()
    )""")
    
    cur.execute("""
    INSERT INTO dba_sanchit.test2 (name,address) 
    select md5(random()::text) as name, md5(random()::text) as address from generate_series(1,10000000);
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def generate_workload():
    """Simulates heavy UPDATE and DELETE operations to create dead tuples."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    while True:
        cur.execute("""
        UPDATE dba_sanchit.test2 
        SET address = 'r3jr243fnoiwe3fc9843we84iu43rtnkj34jbhtbjh43hjbtb34jbtbjh43jht34' 
        WHERE id % 10 = 0""")
        
        cur.execute("DELETE FROM dba_sanchit.test2 WHERE id % 20 = 0")
        conn.commit()
        time.sleep(1)
    
    cur.close()
    conn.close()

def monitor_autovacuum():
    """Monitors autovacuum-related metrics."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    while True:
        cur.execute("""
        SELECT relname, n_dead_tup, last_autovacuum
        FROM pg_stat_all_tables
        WHERE relname = 'test2'""")
        
        for row in cur.fetchall():
            print(f"Table: {row[0]}, Dead Tuples: {row[1]}, Last Autovacuum: {row[2]}")
        
        time.sleep(5)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    setup_database()
    
    # Run workload and monitoring in parallel
    workload_process = Process(target=generate_workload)
    monitor_process = Process(target=monitor_autovacuum)
    
    workload_process.start()
    monitor_process.start()
    
    workload_process.join()
    monitor_process.join()

