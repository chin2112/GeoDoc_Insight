import sqlite3

def check_failures():
    conn = sqlite3.connect('g:/我的雲端硬碟/AGENT/GeoDoc_Insight/data/geodoc.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT case_id, content FROM cases WHERE geocode_status = 'MANUAL_REVIEW_NEEDED' LIMIT 15")
    rows = cur.fetchall()
    
    for r in rows:
        content = r['content'].replace('\n', ' ')
        print(f"[{r['case_id']}]")
        print(f"內容: {content[:200]}...")
        print("-" * 50)

if __name__ == '__main__':
    check_failures()
