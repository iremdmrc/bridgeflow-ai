import sqlite3

DB_PATH = "C:/Users/admin302/Desktop/bridgeflow-ai/agent/patients.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_date TEXT,
            insurance TEXT,
            phone TEXT,
            confirmation_id TEXT
        )
    """)

    conn.commit()
    conn.close()


def seed_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_patients = [
            ("Dwight Schrute", "1970-01-20", "UnitedHealthcare", "7135558899", "CLINIC-10001"),
            ("Pam Beesly", "1979-03-25", "Blue Cross", "7135552244", "CLINIC-10002")
        ]

        cursor.executemany("""
            INSERT INTO patients (name, birth_date, insurance, phone, confirmation_id)
            VALUES (?, ?, ?, ?, ?)
        """, sample_patients)

        conn.commit()

    conn.close()


def find_duplicate_patient(name, birth_date, phone):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, birth_date, insurance, phone, confirmation_id
        FROM patients
        WHERE (LOWER(name) = LOWER(?) AND birth_date = ?)
           OR (LOWER(name) = LOWER(?) AND phone = ?)
        LIMIT 1
    """, (name, birth_date, name, phone))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "name": row[0],
            "birthDate": row[1],
            "insurance": row[2],
            "phone": row[3],
            "confirmationId": row[4]
        }

    return None


def save_patient(name, birth_date, insurance, phone, confirmation_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (name, birth_date, insurance, phone, confirmation_id)
        VALUES (?, ?, ?, ?, ?)
    """, (name, birth_date, insurance, phone, confirmation_id))

    conn.commit()
    conn.close()


def get_recent_patients(limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, birth_date, insurance, phone, confirmation_id
        FROM patients
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "name": row[0],
            "birthDate": row[1],
            "insurance": row[2],
            "phone": row[3],
            "confirmationId": row[4]
        })

    return results