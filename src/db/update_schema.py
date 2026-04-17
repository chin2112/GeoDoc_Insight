import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'geodoc.db')

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if geocode_source exists, if not, add it
    cur.execute("PRAGMA table_info(cases)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'geocode_source' not in columns:
        print("Adding 'geocode_source' column to 'cases' table...")
        cur.execute("ALTER TABLE cases ADD COLUMN geocode_source TEXT")
    
    # Create custom_landmarks table
    print("Creating 'custom_landmarks' table...")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS custom_landmarks (
            name TEXT PRIMARY KEY,
            latitude REAL,
            longitude REAL,
            is_verified BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == '__main__':
    update_schema()
