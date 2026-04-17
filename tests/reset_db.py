import sqlite3

def reset():
    conn = sqlite3.connect('g:/我的雲端硬碟/AGENT/GeoDoc_Insight/data/geodoc.db')
    cur = conn.cursor()
    cur.execute("UPDATE cases SET geocode_status='PENDING' WHERE geocode_status != 'PENDING'")
    conn.commit()
    print("Database reset to PENDING.")

if __name__ == '__main__':
    reset()
