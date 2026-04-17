import os
from src.parser.excel_parser import ExcelParser
from src.db.database import upsert_cases

def process_file(filepath: str, db_path: str = None) -> dict:
    """
    Process an input file, parse its contents, and upsert records into the database.
    
    Args:
        filepath: The path to the file to be processed (.xls, .pdf)
        db_path: Optional custom path to SQLite database.
        
    Returns:
        A dictionary with statistics: {'inserted': int, 'updated': int}
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
        
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext in ['.xls', '.xlsx']:
        parser = ExcelParser()
    elif ext == '.pdf':
        raise NotImplementedError("PDF parser is temporarily suspended as per user request.")
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    cases_records = parser.parse(filepath)
    print(f"[{os.path.basename(filepath)}] Parsed {len(cases_records)} records. Upserting into DB...")
    
    if db_path:
        stats = upsert_cases(cases_records, db_path=db_path)
    else:
        stats = upsert_cases(cases_records)
        
    return stats
