import sqlite3
import os

DB_PATH = os.path.join('data', 'geodoc.db')

def calculate_spatial_severity():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Use rounded coordinates to group cases spatialy (4 decimal places ~ 11m)
    # This ensures cases at the same junction are counted together
    cur.execute("""
        SELECT 
            ROUND(latitude, 4), 
            ROUND(longitude, 4), 
            COUNT(*) as cluster_count 
        FROM cases 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        GROUP BY ROUND(latitude, 4), ROUND(longitude, 4)
    """)
    clusters = cur.fetchall()
    
    print(f"Found {len(clusters)} unique spatial clusters. Updating severity...")
    
    for lat, lng, count in clusters:
        # Score mapping: 
        # 3+ cases = 5.0 (Red)
        # 2 cases = 2.5 (Orange/Yellow)
        # 1 case = 1.0 (Green)
        score = 1.0
        if count == 2:
            score = 2.5
        elif count >= 3:
            score = 5.0
            
        # Update all cases in this spatial cluster
        # Using a small epsilon to handle floating point precision (~11m box)
        cur.execute("""
            UPDATE cases 
            SET severity = ? 
            WHERE ABS(latitude - ?) < 0.0001 AND ABS(longitude - ?) < 0.0001
        """, (score, lat, lng))
    
    conn.commit()
    conn.close()
    print("Spatial severity calculation complete. Labels are now consistent with actual counts.")

if __name__ == "__main__":
    calculate_spatial_severity()
