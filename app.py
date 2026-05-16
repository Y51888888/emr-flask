from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "emr_2026_final_key"

# 病历数据文件
DATA_FILE = "emr_data.json"
emr_data = []

# 程序启动时：读取本地保存的病历文件
def load_data():
    global emr_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            emr_data = json.load(f)
    else:
        emr_data = []

# 保存病历到本地文件
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(emr_data, f, ensure_ascii=False, indent=2)

# 启动先加载数据
load_data()

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
        new_id = max([x.get('id',0) for x in emr_data], default=0)+1
        item = {
            "id": new_id,
            "name": request.form['name'],
            "gender": request.form['gender'],
            "age": request.form['age'],
            "phone": request.form['phone'],
            "visit_time": request.form['visit_time'],
            "chief_complaint": request.form['chief_complaint'],
            "present_history": request.form['present_history'],
            "past_history": request.form['past_history'],
            "allergy_history": request.form['allergy_history'],
            "personal_history": request.form['personal_history'],
            "family_history": request.form['family_history'],
            "physical_exam": request.form['physical_exam'],
            "tcm_diag": request.form['tcm_diag'],
            "syndrome_type": request.form['syndrome_type'],
            "tongue_diag": request.form['tongue_diag'],
            "pulse_diag": request.form['pulse_diag'],
            "therapy_prescription": request.form['therapy_prescription'],
            "follow_up": request.form['follow_up'],
            "doctor_name": request.form['doctor_name']
        }
        emr_data.append(item)
        save_data()   # 新增：添加后自动保存到文件
        return redirect('/')

    key = request.args.get('key','')
    show = [x for x in emr_data if key in x['name'] or key in x['phone']]
    show.sort(key=lambda x:x['id'], reverse=True)
    return render_template('index.html', emr_list=show, key=key)

@app.route('/del/<int:uid>')
def delete(uid):
    if not session.get('login'):
        return redirect('/login')
    global emr_data
    emr_data = [x for x in emr_data if x['id'] != uid]
    save_data()   # 新增：删除后自动保存
    return redirect('/')

@app.route('/edit/<int:uid>', methods=['GET','POST'])
def edit(uid):
    if not session.get('login'):
        return redirect('/login')
    idx = next((i for i,x in enumerate(emr_data) if x['id'] == uid), None)
    if idx is None:
        return redirect('/')
    if request.method == 'POST':
        emr_data[idx] = {
            "id": uid,
            "name": request.form['name'],
            "gender": request.form['gender'],
            "age": request.form['age'],
            "phone": request.form['phone'],
            "visit_time": request.form['visit_time'],
            "chief_complaint": request.form['chief_complaint'],
            "present_history": request.form['present_history'],
            "past_history": request.form['past_history'],
            "allergy_history": request.form['allergy_history'],
            "personal_history": request.form['personal_history'],
            "family_history": request.form['family_history'],
            "physical_exam": request.form['physical_exam'],
            "tcm_diag": request.form['tcm_diag'],
            "syndrome_type": request.form['syndrome_type'],
            "tongue_diag": request.form['tongue_diag'],
            "pulse_diag": request.form['pulse_diag'],
            "therapy_prescription": request.form['therapy_prescription'],
            "follow_up": request.form['follow_up'],
            "doctor_name": request.form['doctor_name']
        }
        save_data()   # 新增：修改后自动保存
        return redirect('/')
    return render_template('edit.html', info=emr_data[idx])

# 查看病历页面
@app.route('/view/<int:uid>')
def view(uid):
    if not session.get('login'):
        return redirect('/login')
    item = next((x for x in emr_data if x['id'] == uid), None)
    if not item:
        return redirect('/')
    return render_template('view.html', item=item)

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
