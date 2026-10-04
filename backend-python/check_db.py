import sqlite3

conn = sqlite3.connect("quality_checker.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Таблицы в БД:", tables)

if not tables:
    print("Таблиц нет! Создаем...")
    from database import init_db
    init_db()
    print("Таблицы созданы")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Теперь таблицы:", cursor.fetchall())
else:
    print("Таблицы есть")

conn.close()