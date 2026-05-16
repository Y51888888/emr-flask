from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "emr_2026_final_key"

# Render 上唯一稳定的持久化路径
DB_PATH = "/tmp/emr_database.db"

# 初始化数据库和表（程序启动时自动执行）
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emr_records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, gender TEXT, age TEXT, phone TEXT,
                  visit_time TEXT, chief_complaint TEXT, present_history TEXT,
                  past_history TEXT, allergy_history TEXT, personal_history TEXT,
                  family_history TEXT, physical_exam TEXT, tcm_diag TEXT,
                  syndrome_type TEXT, tongue_diag TEXT, pulse_diag TEXT,
                  therapy_prescription TEXT, follow_up TEXT, doctor_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 登录账号
USER = "admin"
PWD = "123456"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USER and request.form['pwd'] == PWD:
            session['login'] = True
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/', methods=['GET','POST'])
def index():
    if not session.get('login'):
        return redirect('/login')

    if request.method == 'POST' and request.form.get('action') == 'add':
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO emr_records 
                     (name, gender, age, phone, visit_time, chief_complaint, present_history,
                      past_history, allergy_history, personal_history, family_history,
                      physical_exam, tcm_diag, syndrome_type, tongue_diag, pulse_diag,
                      therapy_prescription, follow_up, doctor_name)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (request.form['name'], request.form['gender'], request.form['age'],
                   request.form['phone'], request.form['visit_time'], request.form['chief_complaint'],
                   request.form['present_history'], request.form['past_history'],
                   request.form['allergy_history'], request.form['personal_history'],
                   request.form['family_history'], request.form['physical_exam'],
                   request.form['tcm_diag'], request.form['syndrome_type'],
                   request.form['tongue_diag'], request.form['pulse_diag'],
                   request.form['therapy_prescription'], request.form['follow_up'],
                   request.form['doctor_name']))
        conn.commit()
        conn.close()
        return redirect('/')

    key = request.args.get('key','')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if key:
        c.execute("SELECT * FROM emr_records WHERE name LIKE ? OR phone LIKE ? ORDER BY id DESC",
                  ('%' + key + '%', '%' + key + '%'))
    else:
        c.execute("SELECT * FROM emr_records ORDER BY id DESC")
    emr_list = [dict(row) for row in c.fetchall()]
    conn.close()

    return render_template('index.html', emr_list=emr_list, key=key)

@app.route('/del/<int:uid>')
def delete(uid):
    if not session.get('login'):
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM emr_records WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:uid>', methods=['GET','POST'])
def edit(uid):
    if not session.get('login'):
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.method == 'POST':
        c.execute('''UPDATE emr_records SET 
                     name=?, gender=?, age=?, phone=?, visit_time=?, chief_complaint=?,
                     present_history=?, past_history=?, allergy_history=?, personal_history=?,
                     family_history=?, physical_exam=?, tcm_diag=?, syndrome_type=?,
                     tongue_diag=?, pulse_diag=?, therapy_prescription=?, follow_up=?, doctor_name=?
                     WHERE id=?''',
                  (request.form['name'], request.form['gender'], request.form['age'],
                   request.form['phone'], request.form['visit_time'], request.form['chief_complaint'],
                   request.form['present_history'], request.form['past_history'],
                   request.form['allergy_history'], request.form['personal_history'],
                   request.form['family_history'], request.form['physical_exam'],
                   request.form['tcm_diag'], request.form['syndrome_type'],
                   request.form['tongue_diag'], request.form['pulse_diag'],
                   request.form['therapy_prescription'], request.form['follow_up'],
                   request.form['doctor_name'], uid))
        conn.commit()
        conn.close()
        return redirect('/')
    c.execute("SELECT * FROM emr_records WHERE id=?", (uid,))
    info = dict(c.fetchone())
    conn.close()
    return render_template('edit.html', info=info)

@app.route('/view/<int:uid>')
def view(uid):
    if not session.get('login'):
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM emr_records WHERE id=?", (uid,))
    item = dict(c.fetchone())
    conn.close()
    return render_template('view.html', item=item)

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
