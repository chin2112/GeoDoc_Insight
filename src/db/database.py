"""Database module for geodoc_insight."""
import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'geodoc.db')

@contextmanager
def get_db_connection(db_path=DB_PATH):
    """Context manager for database connections."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    # Enable dict access for rows
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db(db_path=DB_PATH):
    """Initialize database schema."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        # Create cases table with GIS placeholders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                date_suggested TEXT,
                sequence_no TEXT,
                content TEXT,
                date_dispatch TEXT,
                date_due TEXT,
                date_closed TEXT,
                agency_dept TEXT,
                assignee TEXT,
                reply_status TEXT,
                reply_content TEXT,
                -- GIS Fields for future updates
                address TEXT,
                latitude REAL,
                longitude REAL,
                geocode_status TEXT DEFAULT 'PENDING',
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def upsert_cases(cases_list, db_path=DB_PATH):
    """Upsert a list of cases into the database based on case_id."""
    if not cases_list:
        return {'inserted': 0, 'updated': 0}
        
    init_db(db_path)
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        
        for case in cases_list:
            # Check if case exists
            cursor.execute('SELECT case_id FROM cases WHERE case_id = ?', (case['case_id'],))
            exists = cursor.fetchone() is not None
            
            # Upsert logic
            if exists:
                cursor.execute('''
                    UPDATE cases SET 
                        date_suggested = ?,
                        sequence_no = ?,
                        content = ?,
                        date_dispatch = ?,
                        date_due = ?,
                        date_closed = ?,
                        agency_dept = ?,
                        assignee = ?,
                        reply_status = ?,
                        reply_content = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE case_id = ?
                ''', (
                    case.get('date_suggested'),
                    case.get('sequence_no'),
                    case.get('content'),
                    case.get('date_dispatch'),
                    case.get('date_due'),
                    case.get('date_closed'),
                    case.get('agency_dept'),
                    case.get('assignee'),
                    case.get('reply_status'),
                    case.get('reply_content'),
                    case['case_id']
                ))
                updated += 1
            else:
                cursor.execute('''
                    INSERT INTO cases (
                        case_id, date_suggested, sequence_no, content,
                        date_dispatch, date_due, date_closed,
                        agency_dept, assignee, reply_status, reply_content,
                        geocode_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
                ''', (
                    case['case_id'],
                    case.get('date_suggested'),
                    case.get('sequence_no'),
                    case.get('content'),
                    case.get('date_dispatch'),
                    case.get('date_due'),
                    case.get('date_closed'),
                    case.get('agency_dept'),
                    case.get('assignee'),
                    case.get('reply_status'),
                    case.get('reply_content')
                ))
                inserted += 1
                
        conn.commit()
    
    return {'inserted': inserted, 'updated': updated}
