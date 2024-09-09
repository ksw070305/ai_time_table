from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
import pickle
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    connection = sqlite3.connect("students.db")
    connection.row_factory = sqlite3.Row
    return connection

def load_model(subject):
    model_path = f"C:/project/ai_time_table/models/{subject}(g-t).pkl"
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    return model

def predict_study_time(target_grade):
    # 모델 로드
    korean_model = load_model('korean')
    math_model = load_model('math')
    english_model = load_model('english')

    # 예측 수행
    korean_time = korean_model.predict([[target_grade]])[0]
    math_time = math_model.predict([[target_grade]])[0]
    english_time = english_model.predict([[target_grade]])[0]

    # 한 달 분량으로 변환하고 정수로 반올림
    study_schedule = {
        '국어': round(korean_time * 4),
        '수학': round(math_time * 4),
        '영어': round(english_time * 4)
    }
    return study_schedule

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        print(f"Attempting to login with student_id: {student_id}")  # 디버깅 출력
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        connection.close()
        
        if student:
            session['student_id'] = student_id
            if not student['target_grade']:
                return redirect(url_for('set_target'))
            elif student['study_schedule']:
                return redirect(url_for('view_schedule'))
            else:
                return redirect(url_for('distribute_time'))
        else:
            return "유효하지 않은 학번입니다."
    return render_template('login.html')

@app.route('/set_target', methods=['GET', 'POST'])
def set_target():
    if request.method == 'POST':
        student_id = session.get('student_id')
        target_grade = int(request.form['target_grade'])
        study_schedule = predict_study_time(target_grade)
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE students
            SET target_grade = ?, study_schedule = ?, last_update = ?
            WHERE id = ?
        ''', (target_grade, json.dumps(study_schedule), datetime.now(), student_id))
        connection.commit()
        connection.close()
        
        return redirect(url_for('distribute_time'))
    return render_template('set_target.html')

@app.route('/distribute_time')
def distribute_time():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT study_schedule FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    connection.close()
    
    study_schedule = json.loads(student['study_schedule']) if student['study_schedule'] else {}
    
    return render_template('distribute_time.html', study_schedule=study_schedule)

@app.route('/save_calendar', methods=['POST'])
def save_calendar():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'status': 'error', 'message': '로그인이 필요합니다.'}), 401
    
    calendar_data = request.json.get('calendar')
    if not calendar_data:
        return jsonify({'status': 'error', 'message': '잘못된 데이터입니다.'}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE students SET study_schedule = ? WHERE id = ?', (json.dumps(calendar_data), student_id))
    connection.commit()
    connection.close()
    
    return jsonify({'status': 'success'})

@app.route('/view_schedule')
def view_schedule():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT study_schedule FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    connection.close()
    
    study_schedule = json.loads(student['study_schedule']) if student['study_schedule'] else {}
    current_schedule = {
        '국어': sum([int(event.split(' ')[1].replace('시간', '')) for day in study_schedule for event in day if event.startswith('국어')]),
        '수학': sum([int(event.split(' ')[1].replace('시간', '')) for day in study_schedule for event in day if event.startswith('수학')]),
        '영어': sum([int(event.split(' ')[1].replace('시간', '')) for day in study_schedule for event in day if event.startswith('영어')])
    }
    
    return render_template('view_schedule.html', study_schedule=study_schedule, current_schedule=current_schedule)

@app.route('/reset_targets')
def reset_targets():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE students SET target_grade = NULL, study_schedule = NULL WHERE last_update < ?', (datetime.now() - timedelta(days=180),))
    connection.commit()
    connection.close()
    return "목표 등급이 성공적으로 초기화되었습니다."

def reset_monthly_schedule():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE students SET study_schedule = NULL WHERE strftime("%m", last_update) != strftime("%m", "now")')
    connection.commit()
    connection.close()

@app.before_request
def before_request():
    reset_monthly_schedule()
    reset_targets()

if __name__ == '__main__':
    app.run(debug=True)