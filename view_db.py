import sqlite3

def view_db():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    connection.close()
    
    for student in students:
        print(student)

if __name__ == "__main__":
    view_db()