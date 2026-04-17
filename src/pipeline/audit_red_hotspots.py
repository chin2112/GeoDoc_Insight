import sqlite3
import os
import json

DB_PATH = os.path.join('data', 'geodoc.db')
REPORT_PATH = os.path.join('_docs', 'RED_HOTSPOT_AUDIT_REPORT.json')

def run_audit():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 1. Get all red clusters based on rounded coordinates (4 decimals)
    cur.execute("""
        SELECT 
            ROUND(latitude, 4) as lat, 
            ROUND(longitude, 4) as lng, 
            COUNT(*) as actual_count
        FROM cases 
        WHERE severity = 5.0
        GROUP BY lat, lng
    """)
    clusters = cur.fetchall()
    
    audit_results = []
    print(f"Auditing {len(clusters)} red hotspots...")
    
    for cluster in clusters:
        lat, lng, count = cluster['lat'], cluster['lng'], cluster['actual_count']
        
        # Get all case details in this cluster
        cur.execute("""
            SELECT case_id, content, address, district, dept, severity
            FROM cases 
            WHERE ROUND(latitude, 4) = ROUND(?, 4) AND ROUND(longitude, 4) = ROUND(?, 4)
        """, (lat, lng))
        cases = [dict(r) for r in cur.fetchall()]
        
        # Check for isolated red dots (Critical Bug)
        issue = None
        if len(cases) < 3:
            issue = "INCONSISTENCY: Red marker with fewer than 3 cases."
        
        audit_results.append({
            "coords": [lat, lng],
            "case_count": len(cases),
            "issue": issue,
            "cases": cases
        })
        
    # Save report
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=2)
    
    conn.close()
    print(f"Audit report generated at {REPORT_PATH}")
    return audit_results

if __name__ == "__main__":
    results = run_audit()
    # Simple summary
    issues = [r for r in results if r['issue']]
    print(f"Total issues found: {len(issues)}")
