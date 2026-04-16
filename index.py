from flask import Flask, render_template, request
from datetime import datetime
import random
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# Firebase 初始化
# =========================
if os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
else:
    firebase_config = os.getenv("FIREBASE_CONFIG")
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)

# =========================
# 首頁
# =========================
@app.route("/")
def index():
    homepage = "<h1>老師查詢系統</h1>"
    homepage += "<a href='/mis'>MIS</a><br>"
    homepage += "<a href='/today'>顯示日期時間</a><br>"
    homepage += "<a href='/welcome?u=tcyang&dep=MIS'>傳送使用者暱稱</a><br>"
    homepage += "<a href='/account'>網頁表單傳值</a><br>"
    homepage += "<a href='/about'>子青簡介網頁</a><br>"
    homepage += "<a href='/read'>讀取Firestore資料</a><br>"
    homepage += "<a href='/search'>老師查詢</a><br>"
    return homepage

# =========================
# 基本功能
# =========================
@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href='/'>回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    now_str = f"{now.year}年{now.month}月{now.day}日"
    return render_template("today.html", datetime=now_str)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name=x, dep=y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是 " + user + "；密碼為：" + pwd
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        x = float(request.form["x"])
        y = float(request.form["y"])
        opt = request.form["opt"]

        if opt == "+":
            result = x + y
        elif opt == "-":
            result = x - y
        elif opt == "*":
            result = x * y
        elif opt == "/":
            if y == 0:
                result = "不能除以0"
            else:
                result = x / y
        else:
            result = "運算子錯誤"

        return render_template("math.html", result=result)
    else:
        return render_template("math.html", result=None)

@app.route('/cup', methods=["GET"])
def cup():
    action = request.values.get("action")
    result = None

    if action == 'toss':
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)

        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"

        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }

    return render_template('cup.html', result=result)

# =========================
# 讀取 Firestore 全部資料
# =========================
@app.route("/read")
def read():
    result = ""
    docs = db.collection("靜宜資管").get()

    for doc in docs:
        data = doc.to_dict()
        result += f"姓名：{data.get('name', '')}，研究室：{data.get('lab', '')}<br>"

    return result
@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "").strip()
    result_html = ""

    if keyword:
        docs = db.collection("靜宜資管").get()
        matched = []

        for doc in docs:
            data = doc.to_dict()
            teacher_name = str(data.get("name", ""))
            office = str(data.get("lab", ""))

            if keyword in teacher_name:
                matched.append((teacher_name, office))

        if matched:
            result_html += "<h3>查詢結果：</h3><ul>"
            for name, office in matched:
                result_html += f"<li>{name} - 研究室：{office}</li>"
            result_html += "</ul>"
        else:
            result_html = "<p>查無符合資料</p>"

    return f"""
    <h2>老師查詢系統</h2>
    <form method="get" action="/search">
        <input type="text" name="keyword" placeholder="請輸入老師名字關鍵字" value="{keyword}">
        <input type="submit" value="查詢">
    </form>
    <br>
    {result_html}
    <br>
    <a href="/">回首頁</a>
    """

# =========================
# 主程式
# =========================
if __name__ == "__main__":
    app.run(debug=True)
