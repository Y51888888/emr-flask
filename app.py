from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "emr_2026_final_key"

# 关键：Render 持久化数据库路径（不会被清空）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/emr_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 病历数据表模型
class EmrRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    age = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    visit_time = db.Column(db.String(30))
    chief_complaint = db.Column(db.Text)
    present_history = db.Column(db.Text)
    past_history = db.Column(db.Text)
    allergy_history = db.Column(db.Text)
    personal_history = db.Column(db.Text)
    family_history = db.Column(db.Text)
    physical_exam = db.Column(db.Text)
    tcm_diag = db.Column(db.Text)
    syndrome_type = db.Column(db.Text)
    tongue_diag = db.Column(db.Text)
    pulse_diag = db.Column(db.Text)
    therapy_prescription = db.Column(db.Text)
    follow_up = db.Column(db.Text)
    doctor_name = db.Column(db.String(30))

# 初始化数据表
with app.app_context():
    db.create_all()

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
        new_record = EmrRecord(
            name=request.form['name'],
            gender=request.form['gender'],
            age=request.form['age'],
            phone=request.form['phone'],
            visit_time=request.form['visit_time'],
            chief_complaint=request.form['chief_complaint'],
            present_history=request.form['present_history'],
            past_history=request.form['past_history'],
            allergy_history=request.form['allergy_history'],
            personal_history=request.form['personal_history'],
            family_history=request.form['family_history'],
            physical_exam=request.form['physical_exam'],
            tcm_diag=request.form['tcm_diag'],
            syndrome_type=request.form['syndrome_type'],
            tongue_diag=request.form['tongue_diag'],
            pulse_diag=request.form['pulse_diag'],
            therapy_prescription=request.form['therapy_prescription'],
            follow_up=request.form['follow_up'],
            doctor_name=request.form['doctor_name']
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect('/')

    key = request.args.get('key','')
    if key:
        emr_list = EmrRecord.query.filter(
            EmrRecord.name.contains(key) | EmrRecord.phone.contains(key)
        ).order_by(EmrRecord.id.desc()).all()
    else:
        emr_list = EmrRecord.query.order_by(EmrRecord.id.desc()).all()

    return render_template('index.html', emr_list=emr_list, key=key)

@app.route('/del/<int:uid>')
def delete(uid):
    if not session.get('login'):
        return redirect('/login')
    record = EmrRecord.query.get_or_404(uid)
    db.session.delete(record)
    db.session.commit()
    return redirect('/')

@app.route('/edit/<int:uid>', methods=['GET','POST'])
def edit(uid):
    if not session.get('login'):
        return redirect('/login')
    record = EmrRecord.query.get_or_404(uid)
    if request.method == 'POST':
        record.name = request.form['name']
        record.gender = request.form['gender']
        record.age = request.form['age']
        record.phone = request.form['phone']
        record.visit_time = request.form['visit_time']
        record.chief_complaint = request.form['chief_complaint']
        record.present_history = request.form['present_history']
        record.past_history = request.form['past_history']
        record.allergy_history = request.form['allergy_history']
        record.personal_history = request.form['personal_history']
        record.family_history = request.form['family_history']
        record.physical_exam = request.form['physical_exam']
        record.tcm_diag = request.form['tcm_diag']
        record.syndrome_type = request.form['syndrome_type']
        record.tongue_diag = request.form['tongue_diag']
        record.pulse_diag = request.form['pulse_diag']
        record.therapy_prescription = request.form['therapy_prescription']
        record.follow_up = request.form['follow_up']
        record.doctor_name = request.form['doctor_name']
        db.session.commit()
        return redirect('/')
    return render_template('edit.html', info=record)

@app.route('/view/<int:uid>')
def view(uid):
    if not session.get('login'):
        return redirect('/login')
    item = EmrRecord.query.get_or_404(uid)
    return render_template('view.html', item=item)

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
