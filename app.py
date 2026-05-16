from flask import Flask, render_template, request, redirect, url_for, make_response, session
import pymysql
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io
import os

app = Flask(__name__)
app.json.ensure_ascii = False
app.secret_key = "emr_2026_secret_key_001"

# 数据库配置 适配 Render 环境变量
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "")
DB_PWD = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "")

# 本地调试开关 线上保持 False
LOCAL_MODE = False
if LOCAL_MODE:
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PWD = "123456"
    DB_NAME = "emr_db"

# 后台登录账号密码
LOGIN_USER = "admin"
LOGIN_PWD = "123456"

def get_db():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME,
        charset="utf8mb4"
    )
    return conn

# 病历导出PDF 中文支持
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
        f"姓名：{data[1]}",
        f"性别：{data[2]}",
        f"年龄：{data[3]}",
        f"联系电话：{data[4]}",
        f"就诊时间：{data[5]}",
        f"主诉：{data[6]}",
        f"现病史：{data[7]}",
        f"既往史：{data[8]}",
        f"过敏史：{data[9]}",
        f"个人史：{data[10]}",
        f"家族史：{data[11]}",
        f"体格检查：{data[12]}",
        f"中医诊断：{data[13]}",
        f"证型：{data[14]}",
        f"舌诊：{data[15]}",
        f"脉诊：{data[16]}",
        f"治法方药：{data[17]}",
        f"复诊记录：{data[18]}",
        f"接诊医生：{data[19]}"
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

# 登录
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["pwd"]
        if u == LOGIN_USER and p == LOGIN_PWD:
            session["is_login"] = True
            return redirect(url_for("index"))
    return render_template("login.html")

# 退出
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

# 主页 新增+搜索+列表
@app.route('/', methods=["GET", "POST"])
def index():
    if not session.get("is_login"):
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("action") == "add":
        name = request.form["name"]
        gender = request.form["gender"]
        age = request.form["age"]
        phone = request.form["phone"]
        visit_time = request.form["visit_time"]
        chief_complaint = request.form["chief_complaint"]
        present_history = request.form["present_history"]
        past_history = request.form["past_history"]
        allergy_history = request.form["allergy_history"]
        personal_history = request.form["personal_history"]
        family_history = request.form["family_history"]
        physical_exam = request.form["physical_exam"]
        tcm_diag = request.form["tcm_diag"]
        syndrome_type = request.form["syndrome_type"]
        tongue_diag = request.form["tongue_diag"]
        pulse_diag = request.form["pulse_diag"]
        therapy_prescription = request.form["therapy_prescription"]
        follow_up = request.form["follow_up"]
        doctor_name = request.form["doctor_name"]

        conn = get_db()
        cur = conn.cursor()
        sql = """
        INSERT INTO emr(name,gender,age,phone,visit_time,
        chief_complaint,present_history,past_history,allergy_history,
        personal_history,family_history,physical_exam,
        tcm_diag,syndrome_type,tongue_diag,pulse_diag,
        therapy_prescription,follow_up,doctor_name)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cur.execute(sql, (name,gender,age,phone,visit_time,
        chief_complaint,present_history,past_history,allergy_history,
        personal_history,family_history,physical_exam,
        tcm_diag,syndrome_type,tongue_diag,pulse_diag,
        therapy_prescription,follow_up,doctor_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    key = request.args.get("key", "")
    conn = get_db()
    cur = conn.cursor()
    if key:
        cur.execute("SELECT * FROM emr WHERE name LIKE %s OR phone LIKE %s ORDER BY id DESC", (f"%{key}%", f"%{key}%"))
    else:
        cur.execute("SELECT * FROM emr ORDER BY id DESC")
    emr_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", emr_list=emr_list, key=key)

# 删除病历
@app.route('/del/<int:eid>')
def delete_emr(eid):
    if not session.get("is_login"):
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM emr WHERE id=%s", (eid,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

# 导出PDF
@app.route('/pdf/<int:eid>')
def export_pdf(eid):
    if not session.get("is_login"):
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM emr WHERE id=%s", (eid,))
    data = cur.fetchone()
    cur.close()
    conn.close()

    pdf_file = create_pdf(data)
    resp = make_response(pdf_file.read())
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = f"attachment; filename=病历_{data[1]}.pdf"
    return resp

# 编辑病历
@app.route('/edit/<int:eid>', methods=["GET", "POST"])
def edit_emr(eid):
    if not session.get("is_login"):
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        gender = request.form["gender"]
        age = request.form["age"]
        phone = request.form["phone"]
        visit_time = request.form["visit_time"]
        chief_complaint = request.form["chief_complaint"]
        present_history = request.form["present_history"]
        past_history = request.form["past_history"]
        allergy_history = request.form["allergy_history"]
        personal_history = request.form["personal_history"]
        family_history = request.form["family_history"]
        physical_exam = request.form["physical_exam"]
        tcm_diag = request.form["tcm_diag"]
        syndrome_type = request.form["syndrome_type"]
        tongue_diag = request.form["tongue_diag"]
        pulse_diag = request.form["pulse_diag"]
        therapy_prescription = request.form["therapy_prescription"]
        follow_up = request.form["follow_up"]
        doctor_name = request.form["doctor_name"]

        sql = """
        UPDATE emr SET name=%s,gender=%s,age=%s,phone=%s,visit_time=%s,
        chief_complaint=%s,present_history=%s,past_history=%s,allergy_history=%s,
        personal_history=%s,family_history=%s,physical_exam=%s,
        tcm_diag=%s,syndrome_type=%s,tongue_diag=%s,pulse_diag=%s,
        therapy_prescription=%s,follow_up=%s,doctor_name=%s WHERE id=%s
        """
        cur.execute(sql, (name,gender,age,phone,visit_time,
        chief_complaint,present_history,past_history,allergy_history,
        personal_history,family_history,physical_exam,
        tcm_diag,syndrome_type,tongue_diag,pulse_diag,
        therapy_prescription,follow_up,doctor_name,eid))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.execute("SELECT * FROM emr WHERE id=%s", (eid,))
    info = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit.html", info=info)

# 关键：适配 Render Gunicorn 部署
application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
