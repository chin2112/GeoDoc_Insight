import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'geodoc.db')
EXPORT_PATH = os.path.join(os.path.dirname(__file__), 'data.js')

def export_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Fetch all cases with geocoding
    cur.execute("SELECT * FROM cases")
    cases = [dict(row) for row in cur.fetchall()]
    
    # Fetch pre-calculated analysis results (hotspots)
    cur.execute("SELECT * FROM analysis_summary")
    hotspots = [dict(row) for row in cur.fetchall()]
    
    # Fetch custom landmarks
    cur.execute("SELECT * FROM custom_landmarks")
    landmarks = [dict(row) for row in cur.fetchall()]
    
    # Build final object
    data = {
        "cases": cases,
        "landmarks": landmarks,
        "hotspots": hotspots
    }
    
    # Save as shared JS variable for easy loading without a server if needed
    with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("const APP_DATA = ")
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(";")
        
    print(f"Data exported to {EXPORT_PATH}")
    conn.close()

if __name__ == '__main__':
    export_data()
