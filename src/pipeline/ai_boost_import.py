import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'geodoc.db')

# AI Extracted Data
ai_results = [
    ("南星路101號", 22.5026, 120.3707, "A-EM-2026-47370"),
    ("南京路342巷2號", 22.6146, 120.3448, "A-EM-2026-49381"),
    ("188縣道與鳳頂路口", 22.5932, 120.3541, "A-EM-2026-50315"),
    ("成功路146號", 22.8943, 120.5369, "A-EM-2026-53778"),
    ("環球路77之1號", 22.8465, 120.2705, "A-EM-2026-57804"),
    ("加昌路69橫巷", 22.7216, 120.3177, "A-EM-2026-58765"),
    ("楠梓區後昌路", 22.7115, 120.3015, "A-EM-2026-60783"),
]

def boost_and_learn():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    for name, lat, lon, case_id in ai_results:
        # 1. Add to custom landmarks (Learning)
        print(f"Learning new landmark: {name}")
        cur.execute('''
            INSERT OR REPLACE INTO custom_landmarks (name, latitude, longitude, is_verified)
            VALUES (?, ?, ?, 1)
        ''', (name, lat, lon))
        
        # 2. Update the case record
        cur.execute('''
            UPDATE cases SET address=?, latitude=?, longitude=?, geocode_status='DONE', geocode_source='AI_BOOST'
            WHERE case_id=?
        ''', (f"{name} (AI 學習)", lat, lon, case_id))
        
    conn.commit()
    conn.close()
    print("AI Boost and Learning process completed.")

if __name__ == '__main__':
    boost_and_learn()
