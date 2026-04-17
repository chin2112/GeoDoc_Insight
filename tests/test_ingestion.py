import os
import sys

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.pipeline.ingestion import process_file
from src.db.database import get_db_connection

def test_ingestion():
    test_file_path = r'g:\我的雲端硬碟\AGENT\GeoDoc_Insight\_docs\1999未結案件11501~04.xls'
    print("Testing First Ingestion...")
    stats = process_file(test_file_path)
    print("Stats 1:", stats)
    
    print("\nTesting Second Ingestion (Upsert)...")
    stats2 = process_file(test_file_path)
    print("Stats 2 (should be mostly updates):", stats2)
    
    # Verify in DB
    print("\nVerifying Data in SQLite:")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'geodoc.db')
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cases;")
        count = cursor.fetchone()[0]
        print(f"Total cases in DB: {count}")
        
        cursor.execute("SELECT case_id, sequence_no, date_suggested, agency_dept, geocode_status FROM cases LIMIT 2;")
        rows = cursor.fetchall()
        for i, row in enumerate(rows):
            print(f"Row {i+1}: {dict(row)}")

if __name__ == '__main__':
    test_ingestion()
