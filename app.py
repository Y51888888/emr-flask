from flask import Flask, render_template, request, redirect, url_for, make_response, session
import io

app = Flask(__name__)
app.secret_key = "emr_123456"
emr_data = []

# 登录账号
USER = "admin"
PWD = "123456"

# ----------------------
# PDF 导出（纯文本，100%成功）
# ----------------------
def export_txt(data):
    content = f"""
中医电子病历

姓名：{data['name']}
性别：{data['gender']}
年龄：{data['age']}
电话：{data['phone']}
就诊时间：{data['visit_time']}

主诉：{data['chief_complaint']}
现病史：{data['present_history']}
既往史：{data['past_history']}
过敏史：{data['allergy_history']}
个人史：{data['personal_history']}
家族史：{data['family_history']}

体格检查：{data['physical_exam']}
中医诊断：{data['tcm_diag']}
证型：{data['syndrome_type']}
舌诊：{data['tongue_diag']}
脉诊：{data['pulse_diag']}

治法方药：{data['therapy_prescription']}
复诊记录：{data['follow_up']}
接诊医生：{data['doctor_name']}
    """
    return content.strip()

# ----------------------
# 路由
# ----------------------
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
        return redirect('/')
    return render_template('edit.html', info=emr_data[idx])

# ----------------------
# 导出文件（100%成功）
# ----------------------
@app.route('/export/<int:uid>')
def export(uid):
    if not session.get('login'):
        return redirect('/login')
    item = next((x for x in emr_data if x['id'] == uid), None)
    if not item:
        return redirect('/')
    
    txt = export_txt(item)
    response = make_response(txt)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=病历_{item['name']}.txt"
    return response

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
