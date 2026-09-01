import sqlite3
import jdatetime  # برای تاریخ شمسی (حتما نصبش کن: pip install jdatetime)

def get_db():
    conn = sqlite3.connect('data.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            category TEXT,
            description TEXT,
            trans_type TEXT,  -- 'income' یا 'expense'
            date_shamsi TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def add_transaction(user_id, amount, category, desc, trans_type):
    conn = get_db()
    today = jdatetime.date.today().strftime("%Y/%m/%d")
    conn.execute(
        "INSERT INTO transactions (user_id, amount, category, description, trans_type, date_shamsi) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, amount, category, desc, trans_type, today)
    )
    conn.commit()
    conn.close()

def get_monthly_summary(user_id):
    conn = get_db()
    # اینجا مجموع درآمد و هزینه‌های ماه جاری رو برمی‌گردونه
    cursor = conn.execute(
        "SELECT trans_type, SUM(amount) FROM transactions WHERE user_id = ? AND strftime('%m', timestamp) = strftime('%m', 'now') GROUP BY trans_type",
        (user_id,)
    )
    data = cursor.fetchall()
    conn.close()
    return data