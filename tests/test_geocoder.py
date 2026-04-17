import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.pipeline.geocoding_job import run_geocoding_batch
from src.db.database import get_db_connection

def verify_20_records():
    print("=== TIER 2 PIPELINE VERIFICATION (20 RECORDS) ===\n")
    
    # Run the batch job for exactly 20 records
    run_geocoding_batch(limit=20)
    
    # Read the updated output visually
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Get 20 rows that we just touched (not PENDING)
        cursor.execute('''
        SELECT content, address, latitude, longitude, geocode_status 
        FROM cases 
        WHERE geocode_status != 'PENDING' 
        LIMIT 20
        ''')
        rows = cursor.fetchall()
        
    print("\n--- RESULTS PREVIEW ---")
    for i, row in enumerate(rows):
        content_brief = row['content'][:50].replace('\n', ' ') + '...'
        status = row['geocode_status']
        addr = row['address'] or 'N/A'
        coords = f"({row['latitude']}, {row['longitude']})" if row['latitude'] else "N/A"
        
        icon = "✅" if status == 'DONE' else "⚠️"
        print(f"[{i+1}] {icon} Status: {status}")
        print(f"    Raw: {content_brief}")
        print(f"    Mapped Location: {addr}")
        print(f"    Coordinates    : {coords}")
        print("-" * 40)

if __name__ == '__main__':
    verify_20_records()
