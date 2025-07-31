from flask import Flask, render_template, request, send_file
import pandas as pd
import qrcode
import os
from datetime import datetime

app = Flask(__name__)
os.makedirs('static/qr_codes', exist_ok=True)

student_data=pd.read_csv("student_data.csv")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate_qr():
    if request.method == 'POST':
        name = request.form['name'].strip()
        student_id = request.form['id'].strip()
        if not name or not student_id:
            return render_template('generate.html', error="Name and ID required")
        qr_data = f"{name}|{student_id}"
        img = qrcode.make(qr_data)
        filename = f"{student_id}_{name}.png"
        path = os.path.join('static/qr_codes', filename)
        img.save(path)

        if os.path.exists('student_data'):
            df = pd.read_csv('student_data')
        else:
            df = pd.DataFrame(columns=['Name', 'ID'])

        if not ((df['ID'] == student_id) & (df['Name'] == name)).any():
            df = pd.concat([df, pd.DataFrame([{'Name': name, 'ID': student_id}])], ignore_index=True)
            df.to_csv('student_data', index=False)

        return send_file(path, as_attachment=True, download_name=filename)
    return render_template('generate.html', error=None)

@app.route('/scan')
def scan_page():
    return render_template('scan.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.json.get('data')
    if data and '|' in data:
        name, student_id = data.split('|', 1)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if os.path.exists('attendance.csv'):
            df = pd.read_csv('attendance.csv')
        else:
            df = pd.DataFrame(columns=['Name', 'ID', 'Time'])

        today = now[:10]
        if not ((df['ID'] == student_id) & (df['Time'].str.startswith(today))).any():
            df = pd.concat([df, pd.DataFrame([{'Name': name, 'ID': student_id, 'Time': now}])], ignore_index=True)
            df.to_csv('attendance.csv', index=False)
            return {'status': 'success', 'message': f'Attendance marked for {name}'}
        else:
            return {'status': 'info', 'message': f'{name} is already marked today.'}
    return {'status': 'error', 'message': 'Invalid QR data'}

if __name__ == '__main__':
    app.run(debug=True)
