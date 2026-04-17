import sqlite3
import os

DB_PATH = os.path.join('data', 'geodoc.db')

def diagnose_case(case_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get target case
    cur.execute("SELECT case_id, latitude, longitude, severity FROM cases WHERE case_id = ?", (case_id,))
    target = cur.fetchone()
    if not target:
        print(f"Case {case_id} not found.")
        return
    
    id_, lat, lng, sev = target
    print(f"Target: {id_}, Coords: {lat}, {lng}, Severity: {sev}")
    
    # Exact grouping like frontend (toFixed 5)
    target_lat_5 = round(lat, 5)
    target_lng_5 = round(lng, 5)
    
    cur.execute("""
        SELECT case_id FROM cases 
        WHERE ROUND(latitude, 5) = ROUND(?, 5) 
          AND ROUND(longitude, 5) = ROUND(?, 5)
    """, (lat, lng))
    nearby = cur.fetchall()
    
    print(f"Cases at the SAME rounded coords (5 decimals): {[r[0] for r in nearby]}")
    print(f"Total count: {len(nearby)}")
    
    conn.close()

if __name__ == "__main__":
    diagnose_case("A-EM-2026-50744")
