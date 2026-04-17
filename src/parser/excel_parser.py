import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any
from .base import BaseParser

class ExcelParser(BaseParser):
    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        # Read with pandas. Use 'xlrd' engine for older .xls files.
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            df = pd.read_excel(filepath, engine='xlrd')
            
        cases = []
        
        # In this specific report format, we need to locate the actual header row.
        # The true header contains "建議日期" or similar.
        header_row_idx = None
        for idx, row in df.iterrows():
            row_str = str(row.values)
            if "建議日期" in row_str and "案號" in row_str:
                header_row_idx = idx
                break
                
        if header_row_idx is not None:
            # We skip until the record starts, which is normally the row after the header.
            start_idx = header_row_idx + 1
        else:
            # Fallback if header not found
            start_idx = 0
            
        for i in range(start_idx, len(df)):
            row = df.iloc[i]
            
            # The columns in the file do not perfectly map to simple headers due to merged columns.
            # Using position-based mapping based on observation:
            # col 1: 日期\n案號\n序號
            # col 2: 建議內容
            # col 3: 分文日期\n應結案日期\n結案日期
            # col 4: 機關名稱\n科室\n承辦人及電話
            # col 5: 管制情形/答覆日期\n答覆內容
            
            col1 = str(row.iloc[1]) if not pd.isna(row.iloc[1]) else ""
            col2 = str(row.iloc[2]) if not pd.isna(row.iloc[2]) else ""
            col3 = str(row.iloc[3]) if not pd.isna(row.iloc[3]) else ""
            col4 = str(row.iloc[4]) if not pd.isna(row.iloc[4]) else ""
            col5 = str(row.iloc[5]) if not pd.isna(row.iloc[5]) else ""
            
            if not col1.strip() or col1 == 'nan':
                continue
                
            # Extract Case ID
            case_id_match = re.search(r'([A-Z]-\w+-\d+-\d+)', col1)
            case_id = case_id_match.group(1) if case_id_match else None
            
            if not case_id:
                # If no case ID is found, it's probably not a valid record row
                continue
                
            dates_col1 = re.findall(r'\d{4}-\d{2}-\d{2}', col1)
            date_suggested = dates_col1[0] if dates_col1 else ""
            
            seq_no_match = re.search(r'\n(\d{2}-\d+)', col1)
            sequence_no = seq_no_match.group(1) if seq_no_match else ""
            
            dates_col3 = re.findall(r'\d{4}-\d{2}-\d{2}', col3)
            date_dispatch = dates_col3[0] if len(dates_col3) > 0 else ""
            date_due = dates_col3[1] if len(dates_col3) > 1 else ""
            date_closed = dates_col3[2] if len(dates_col3) > 2 else ""
            
            content = col2.strip()
            
            agency_dept = ""
            assignee = ""
            col4_parts = [p.strip() for p in col4.split('\n') if p.strip()]
            if len(col4_parts) > 0:
                agency_dept = " / ".join(col4_parts[:-1]) if len(col4_parts) > 1 else col4_parts[0]
                assignee = col4_parts[-1]
                
            reply_status = ""
            reply_content = ""
            col5_parts = col5.split('\n', 1)
            if len(col5_parts) > 0:
                reply_status = col5_parts[0].strip()
            if len(col5_parts) > 1:
                reply_content = col5_parts[1].strip()
                
            case_record = {
                'case_id': case_id.strip(),
                'date_suggested': date_suggested.strip(),
                'sequence_no': sequence_no.strip(),
                'content': content,
                'date_dispatch': date_dispatch.strip(),
                'date_due': date_due.strip(),
                'date_closed': date_closed.strip(),
                'agency_dept': agency_dept.strip(),
                'assignee': assignee.strip(),
                'reply_status': reply_status,
                'reply_content': reply_content
            }
            cases.append(case_record)
            
        return cases
