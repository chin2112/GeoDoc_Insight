import sqlite3

def dump_results():
    conn = sqlite3.connect('g:/我的雲端硬碟/AGENT/GeoDoc_Insight/data/geodoc.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT case_id, substr(content, 1, 40) as content_brief, address, latitude, longitude, geocode_status FROM cases WHERE geocode_status != 'PENDING' LIMIT 20")
    rows = cur.fetchall()
    
    out = ['# 抽測 20 筆位址辨識結果\n| 案號 | 內容摘要 (前40字) | 辨識結果 | 座標 | 狀態 |\n|---|---|---|---|---|']
    for r in rows:
        cb = r['content_brief'].replace('\n', '')
        addr = r['address'] if r['address'] else '-'
        coords = f"{r['latitude']},{r['longitude']}" if r['latitude'] else '-'
        out.append(f"| {r['case_id']} | {cb} | {addr} | {coords} | {r['geocode_status']} |")
        
    md_path = 'C:/Users/chin211/.gemini/antigravity/brain/097de000-4a07-4dbe-9a96-0761259ef201/walkthrough.md'
    with open(md_path, 'a', encoding='utf-8') as f:
        f.write('\n\n' + '\n'.join(out))
    
    print("Marked 20 cases appended to Walkthrough.")

if __name__ == '__main__':
    dump_results()
