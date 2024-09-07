import sqlite3

def init_db():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            grade INTEGER,
            class INTEGER,
            number INTEGER,
            target_grade TEXT,
            study_schedule TEXT,
            last_update DATE
        )
    ''')
    
    # 학번 생성 (1학년부터 3학년, 1반부터 9반, 1번부터 40번)
    for grade in range(1, 4):
        for class_num in range(1, 10):
            for number in range(1, 41):
                student_id = int(f"{grade}{class_num:02d}{number:02d}")
                cursor.execute('''
                    INSERT INTO students (id, grade, class, number)
                    VALUES (?, ?, ?, ?)
                ''', (student_id, grade, class_num, number))
    
    connection.commit()
    connection.close()

if __name__ == "__main__":
    init_db()