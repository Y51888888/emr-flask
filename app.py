from flask import Flask, render_template, request, redirect, url_for, make_response, session
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io

app = Flask(__name__)
app.json.ensure_ascii = False
app.secret_key = "emr_2026_secret_key_001"

# 全部存在内存里！不写文件！不报错！
emr_memory_list = []

LOGIN_USER = "admin"
LOGIN_PWD = "123456"

def create_pdf(data):
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    c.setFont('STSong-Light', 12)
    y = 780
    line_height = 22
    c.drawString(80, y, "中医电子病历")
    y -= line_height
    fields = [
        f"姓名：{data['name']}",
        f"性别：{data['gender']}",
        f"年龄：{data['age']}",
        f"电话：{data['phone']}",
        f"就诊时间：{data['visit_time']}",
        f"主诉：{data['chief_complaint']}",
        f"现病史：{data['present_history']}",
        f"既往史：{data['past_history']}",
        f"过敏史：{data['allergy_history']}",
        f"个人史：{data['personal_history']}",
        f"家族史：{data['family_history']}",
        f"体格检查：{data['physical_exam']}",
        f"中医诊断：{data['tcm_diag']}",
        f"证型：{data['syndrome_type']}",
        f"舌诊：{data['tongue_diag']}",
        f"脉诊：{data['pulse_diag']}",
        f"治法方药：{data['therapy_prescription']}",
        f"复诊记录：{data['follow_up']}",
        f"医生：{data['doctor_name']}"
    ]
    for txt in fields:
        if y < 50:
            c.showPage()
            c.setFont('STSong-Light', 12)
            y = 780
        c.drawString(40, y, txt)
        y -= line_height
    c.save()
    buf.seek(0)
    return buf

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["pwd"]
        if u == LOGIN_USER and p == LOGIN_PWD:
            session["login"] = True
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/', methods=["GET","POST"])
def index():
    global emr_memory_list
    if not session.get("login"):
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("action")=="add":
        new_id = max([x.get("id",0) for x in emr_memory_list], default=0)+1
        item = {
            "id": new_id,
            "name": request.form["name"],
            "gender": request.form["gender"],
            "age": request.form["age"],
            "phone": request.form["phone"],
            "visit_time": request.form["visit_time"],
            "chief_complaint": request.form["chief_complaint"],
            "present_history": request.form["present_history"],
            "past_history": request.form["past_history"],
            "allergy_history": request.form["allergy_history"],
            "personal_history": request.form["personal_history"],
            "family_history": request.form["family_history"],
            "physical_exam": request.form["physical_exam"],
            "tcm_diag": request.form["tcm_diag"],
            "syndrome_type": request.form["syndrome_type"],
            "tongue_diag": request.form["tongue_diag"],
            "pulse_diag": request.form["pulse_diag"],
            "therapy_prescription": request.form["therapy_prescription"],
            "follow_up": request.form["follow_up"],
            "doctor_name": request.form["doctor_name"]
        }
        emr_memory_list.append(item)
        return redirect(url_for("index"))

    key = request.args.get("key","")
    show_list = []
    for x in emr_memory_list:
        if key and key not in x["name"] and key not in x["phone"]:
            continue
        show_list.append(x)
    show_list.sort(key=lambda x:x["id"], reverse=True)
    return render_template("index.html", emr_list=show_list, key=key)

@app.route('/del/<int:uid>')
def delete(uid):
    global emr_memory_list
    if not session.get("login"):
        return redirect(url_for("login"))
    new_list = [x for x in emr_memory_list if x["id"]!=uid]
    emr_memory_list = new_list
    return redirect(url_for("index"))

@app.route('/pdf/<int:uid>')
def pdf(uid):
    global emr_memory_list
    if not session.get("login"):
        return redirect(url_for("login"))
    item = None
    for x in emr_memory_list:
        if x["id"] == uid:
            item = x
            break
    if not item:
        return redirect(url_for("index"))
    pdf_buf = create_pdf(item)
    resp = make_response(pdf_buf.read())
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = f"attachment; filename=病历_{item['name']}.pdf"
    return resp

@app.route('/edit/<int:uid>', methods=["GET","POST"])
def edit(uid):
    global emr_memory_list
    if not session.get("login"):
        return redirect(url_for("login"))
    idx = -1
    for i in range(len(emr_memory_list)):
        if emr_memory_list[i]["id"] == uid:
            idx = i
            break
    if idx < 0:
        return redirect(url_for("index"))

    if request.method == "POST":
        emr_memory_list[idx] = {
            "id": uid,
            "name": request.form["name"],
            "gender": request.form["gender"],
            "age": request.form["age"],
            "phone": request.form["phone"],
            "visit_time": request.form["visit_time"],
            "chief_complaint": request.form["chief_complaint"],
            "present_history": request.form["present_history"],
            "past_history": request.form["past_history"],
            "allergy_history": request.form["allergy_history"],
            "personal_history": request.form["personal_history"],
            "family_history": request.form["family_history"],
            "physical_exam": request.form["physical_exam"],
            "tcm_diag": request.form["tcm_diag"],
            "syndrome_type": request.form["syndrome_type"],
            "tongue_diag": request.form["tongue_diag"],
            "pulse_diag": request.form["pulse_diag"],
            "therapy_prescription": request.form["therapy_prescription"],
            "follow_up": request.form["follow_up"],
            "doctor_name": request.form["doctor_name"]
        }
        return redirect(url_for("index"))
    return render_template("edit.html", info=emr_memory_list[idx])

application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
