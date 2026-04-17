import sqlite3
import os
import re

DB_PATH = os.path.join('data', 'geodoc.db')

DISTRICTS = [
    '楠梓', '左營', '鼓山', '三民', '苓雅', '新興', '前金', '鹽埕', '前鎮', '小港', 
    '鳳山', '鳥松', '大寮', '林園', '大樹', '仁武', '大社', '岡山', '橋頭', '燕巢', 
    '阿蓮', '路竹', '湖內', '茄萣', '永安', '彌陀', '梓官', '旗山', '美濃', '六龜', 
    '甲仙', '杉林', '內門', '茂林', '桃源', '那瑪夏'
]

DEPT_MAPPING = {
    '交通工程科': ['號誌', '標線', '紅綠燈', '劃線', '燈號', '路平', '坑洞', '路面'],
    '停車管理中心': ['停車', '違停', '紅線', '車位', '格位', '停車場'],
    '交通管制工程處': ['執法', '取締', '科技執法', '罰單', '警察', '測照'],
    '運輸規劃科': ['公車', '捷運', '站牌', '轉乘', '規劃', '公車亭']
}

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(cases)")
    cols = [c[1] for c in cur.fetchall()]
    
    new_cols = {
        'district': 'TEXT',
        'category': 'TEXT',
        'dept': 'TEXT',
        'suggestion_date': 'DATE'
    }
    
    for col, type_ in new_cols.items():
        if col not in cols:
            print(f"Adding column {col}...")
            cur.execute(f"ALTER TABLE cases ADD COLUMN {col} {type_}")
    
    conn.commit()
    conn.close()

def enrich_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT case_id, content, address, date_suggested FROM cases")
    rows = cur.fetchall()
    
    for row in rows:
        case_id = row['case_id']
        content = row['content']
        address = row['address'] or ""
        text = content + address
        
        # 1. District Extraction
        district = "未知"
        for d in DISTRICTS:
            if d in text:
                district = d + "區"
                break
        
        # 2. Category & Dept Mapping
        category = "其他"
        dept = "未分類"
        
        for d_name, keywords in DEPT_MAPPING.items():
            if any(k in text for k in keywords):
                dept = d_name
                category = keywords[0] # Use first keyword as representative category for now
                break
        
        # 3. Clean Date
        # Assume format like YYYY-MM-DD
        raw_date = row['date_suggested']
        clean_date = raw_date[:10] if raw_date else "2026-04-01"
        
        cur.execute("""
            UPDATE cases 
            SET district=?, category=?, dept=?, suggestion_date=?
            WHERE case_id=?
        """, (district, category, dept, clean_date, case_id))
        
    conn.commit()
    conn.close()
    print("Business data enrichment complete.")

if __name__ == "__main__":
    update_schema()
    enrich_data()
