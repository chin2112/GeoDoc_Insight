import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'geodoc.db')

def run_analytics():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("Starting Analytics Engine v2 (Spatial Persistence)...")
    
    # 1. Clear previous results
    cur.execute("DELETE FROM analysis_summary")
    
    # 2. Extract spatial clusters (using 4 decimal places ~11m as standard junction)
    cur.execute("""
        SELECT 
            ROUND(latitude, 4) as lat, 
            ROUND(longitude, 4) as lng, 
            COUNT(*) as count,
            GROUP_CONCAT(case_id) as ids,
            GROUP_CONCAT(COALESCE(address, '')) as addresses,
            GROUP_CONCAT(COALESCE(district, '')) as districts
        FROM cases 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        GROUP BY lat, lng
    """)
    clusters = cur.fetchall()
    
    for cluster in clusters:
        lat, lng, count = cluster['lat'], cluster['lng'], cluster['count']
        
        # Scoring logic
        severity = 1.0
        if count == 2:
            severity = 2.5
        elif count >= 3:
            severity = 5.0
            
        # Determine primary address (longest string usually contains more detail)
        addr_list = [a for a in cluster['addresses'].split(',') if a]
        primary_address = max(addr_list, key=len) if addr_list else "未知路口"
        
        # Determine primary district
        dist_list = [d for d in cluster['districts'].split(',') if d]
        primary_district = max(set(dist_list), key=dist_list.count) if dist_list else "未知"
        
        # Insert into summary table
        cur.execute("""
            INSERT INTO analysis_summary (lat, lng, case_count, severity, case_ids, district, primary_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (lat, lng, count, severity, cluster['ids'], primary_district, primary_address))
        
        # Sync back to individual cases in this cluster
        cur.execute("""
            UPDATE cases 
            SET severity = ? 
            WHERE ABS(latitude - ?) < 0.0001 AND ABS(longitude - ?) < 0.0001
        """, (severity, lat, lng))

    conn.commit()
    conn.close()
    print(f"Analytics complete. {len(clusters)} hotspots persisted.")

if __name__ == "__main__":
    run_analytics()
