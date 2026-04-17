import sqlite3

def check_failures():
    conn = sqlite3.connect('g:/我的雲端硬碟/AGENT/GeoDoc_Insight/data/geodoc.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT case_id, content FROM cases WHERE geocode_status = 'MANUAL_REVIEW_NEEDED' LIMIT 15")
    rows = cur.fetchall()
    
    out = []
    for r in rows:
        content = r['content'].replace('\n', ' ')
        out.append(f"### [{r['case_id']}]")
        out.append(f"內容: {content}")
        out.append("-" * 50)
        
    with open('C:/Users/chin211/.gemini/antigravity/brain/097de000-4a07-4dbe-9a96-0761259ef201/failed_cases.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

if __name__ == '__main__':
    check_failures()
