import sqlite3 as sql

DB_PATH = "C:\\Users\\ignac\\Desktop\\Argenway\\APP_STREAMERS\\database\\streamers.db"

def createDB():
    conn = sql.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE streamers (
        name TEXT,
        subs INTEGER,
        followers INTEGER        
    )""")
    conn.commit()
    conn.close()
        
def addValues():
    conn = sql.connect(DB_PATH)
    cursor = conn.cursor()
    data = [
        ("alexelcapo", 10000, 800000),
        ("ibai", 25000, 7000000),
        ("elxokas", 10000, 1000000),
        ("auronplay", 20000, 8000000),
        ("cristinini", 5500, 3000000)
    ]
    cursor.executemany("""INSERT INTO streamers VALUES (?,?,?)""", data)
    conn.commit()
    conn.close()    
       

if __name__ == "__main__":
    createDB()
    addValues()