import os
import sqlite3
from datetime import date

DB_NAME = "ramadan_bot.db"
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_xp (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_check (
        user_id INTEGER,
        date TEXT,
        checked INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, date)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spiritual_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fitness_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task_id INTEGER,
        task_type TEXT,
        date TEXT,
        UNIQUE(user_id, task_id, date, task_type)
    )
    """)
    conn.commit()


def init_tasks():
    spiritual = [
        "Bomdod in mosque",
        "Taroveh in mosque",
        "1000 zikr/salovat/istighfor",
        "15 pages tafsir",
        "1 juz Quran"
    ]
    fitness = [
        "50 pushups",
        "50 squats",
        "50 press",
        "10k steps walking"
    ]

    for name in spiritual:
        cursor.execute("SELECT id FROM spiritual_tasks WHERE name=?", (name,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO spiritual_tasks (name) VALUES (?)", (name,))

    for name in fitness:
        cursor.execute("SELECT id FROM fitness_tasks WHERE name=?", (name,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO fitness_tasks (name) VALUES (?)", (name,))
    conn.commit()

if not os.path.exists(DB_NAME):
    init_db()
    init_tasks()



def add_user(user_id, name):
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()


def get_tasks(task_type):
    table = "spiritual_tasks" if task_type == "spiritual" else "fitness_tasks"
    cursor.execute(f"SELECT id, name FROM {table}")
    return cursor.fetchall()


def mark_done(user_id, task_id, task_type):
    today_str = date.today().isoformat()
    cursor.execute(
        "INSERT OR IGNORE INTO progress (user_id, task_id, task_type, date) VALUES (?, ?, ?, ?)",
        (user_id, task_id, task_type, today_str)
    )
    conn.commit()


def get_progress(user_id, task_type):
    today_str = date.today().isoformat()
    table = "spiritual_tasks" if task_type == "spiritual" else "fitness_tasks"
    cursor.execute(f"SELECT id, name FROM {table}")
    tasks = cursor.fetchall()
    result = []
    for task_id, name in tasks:
        cursor.execute(
            "SELECT id FROM progress WHERE user_id=? AND task_id=? AND task_type=? AND date=?",
            (user_id, task_id, task_type, today_str)
        )
        done = bool(cursor.fetchone())
        result.append((name, done))
    return result


def is_task_done_today(user_id, task_id, task_type):
    today_str = date.today().isoformat()
    cursor.execute("""
        SELECT 1 FROM progress 
        WHERE user_id=? AND task_id=? AND task_type=? AND date=?
    """, (user_id, task_id, task_type, today_str))
    return cursor.fetchone() is not None


def get_report_table():
    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT name FROM spiritual_tasks")
    spiritual_tasks = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT name FROM fitness_tasks")
    fitness_tasks = [row[0] for row in cursor.fetchall()]
    all_tasks = spiritual_tasks + fitness_tasks

    cursor.execute("SELECT DISTINCT date FROM progress ORDER BY date")
    all_dates = [row[0] for row in cursor.fetchall()]

    report = []

    for user_id, name in users:
        for day in all_dates:
            row = {"Имя пользователя": name, "Дата": day}
            all_done = True
            for task in all_tasks:
                cursor.execute("SELECT id FROM spiritual_tasks WHERE name=?", (task,))
                res = cursor.fetchone()
                task_type = "spiritual" if res else "fitness"
                task_id = res[0] if res else cursor.execute("SELECT id FROM fitness_tasks WHERE name=?", (task,)).fetchone()[0]

                cursor.execute(
                    "SELECT id FROM progress WHERE user_id=? AND task_id=? AND task_type=? AND date=?",
                    (user_id, task_id, task_type, day)
                )
                done = bool(cursor.fetchone())
                row[task] = "✅" if done else "❌"
                if not done:
                    all_done = False

            row["Все задачи выполнены?"] = "✅" if all_done else "❌"
            report.append(row)

    return report, all_tasks


LEVELS = [
    (1, 0),
    (2, 150),
    (3, 400),
    (4, 800),
    (5, 1400)
]


def calculate_level(xp: int) -> int:
    level = 1
    for lvl, threshold in LEVELS:
        if xp >= threshold:
            level = lvl
        else:
            break
    return level


def get_user_xp(user_id: int):
    cursor.execute("SELECT xp, level FROM user_xp WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO user_xp (user_id, xp, level) VALUES (?, 0, 1)", (user_id,))
        conn.commit()
        return 0, 1
    return row


def add_xp(user_id: int, amount: int):
    xp, _ = get_user_xp(user_id)
    new_xp = max(0, xp + amount)
    new_level = calculate_level(new_xp)

    cursor.execute("""
        INSERT INTO user_xp (user_id, xp, level)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET xp=?, level=?
    """, (user_id, new_xp, new_level, new_xp, new_level))
    conn.commit()

    return new_xp, new_level


def get_today_progress(user_id: int):
    today = date.today().isoformat()

    cursor.execute("SELECT COUNT(*) FROM spiritual_tasks")
    total_spiritual = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM fitness_tasks")
    total_fitness = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM progress
        WHERE user_id=? AND task_type='spiritual' AND date=?
    """, (user_id, today))
    done_spiritual = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM progress
        WHERE user_id=? AND task_type='fitness' AND date=?
    """, (user_id, today))
    done_fitness = cursor.fetchone()[0]

    return done_spiritual, total_spiritual, done_fitness, total_fitness


def apply_daily_penalty(user_id: int):
    """Применяем штраф, если пользователь ничего не сделал сегодня."""
    today_str = date.today().isoformat()

    cursor.execute("SELECT checked FROM daily_check WHERE user_id=? AND date=?", (user_id, today_str))
    if cursor.fetchone():
        return

    cursor.execute("SELECT 1 FROM progress WHERE user_id=? AND date=? LIMIT 1", (user_id, today_str))
    did_anything = cursor.fetchone() is not None

    if not did_anything:
        add_xp(user_id, -10)  # штраф за пропуск

    cursor.execute("INSERT INTO daily_check (user_id, date, checked) VALUES (?, ?, 1)", (user_id, today_str))
    conn.commit()


def get_level_name(level: int) -> str:
    return {
        1: "🌱 Начало",
        2: "🔥 В пути",
        3: "💪 Укрепился",
        4: "🏆 Стабильность",
        5: "👑 Мастер Рамадана"
    }.get(level, "🌱 Начало")


def get_user_profile(user_id: int):
    cursor.execute("""
        SELECT xp, level FROM user_xp
        WHERE user_id=?
    """, (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "INSERT INTO user_xp (user_id, xp, level) VALUES (?, 0, 1)",
            (user_id,)
        )
        conn.commit()
        return 0, 1
    return row
