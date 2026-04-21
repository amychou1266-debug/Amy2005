from flask import Flask, render_template, request
from datetime import datetime
import random
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from bs4 import BeautifulSoup

# =========================
# Firebase 初始化
# =========================
if os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
else:
    firebase_config = os.getenv("FIREBASE_CONFIG")
    if firebase_config is None:
        raise ValueError("找不到 serviceAccountKey.json，也沒有設定 FIREBASE_CONFIG")
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
    homepage = "<h1>這是網站</h1>"
    homepage += "<a href='/mis'>MIS</a><br>"
    homepage += "<a href='/today'>顯示日期時間</a><br>"
    homepage += "<a href='/welcome?u=tcyang&dep=MIS'>傳送使用者暱稱</a><br>"
    homepage += "<a href='/account'>網頁表單傳值</a><br>"
    homepage += "<a href='/about'>我的簡介網頁</a><br>"
    homepage += "<a href='/cup'>擲筊</a><br>"
    homepage += "<a href='/read'>讀取Firestore資料</a><br>"
    homepage += "<a href='/search'>老師查詢</a><br>"
    homepage += "<a href='/spider1'>爬蟲</a><br>"
    homepage += "<a href='/movie'>查詢即將上映電影</a><br>"
    return homepage

# =========================
# 基本功能
# =========================
@app.route("/mis")
def mis():
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
        return f"您輸入的帳號是 {user}；密碼為：{pwd}"
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
            result = "不能除以0" if y == 0 else x / y
        else:
            result = "運算子錯誤"

        return render_template("math.html", result=result)
    else:
        return render_template("math.html", result=None)

@app.route("/cup", methods=["GET"])
def cup():
    action = request.values.get("action")
    result = None

    if action == "toss":
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)

        if x1 != x2:
            msg = "聖筊：表示神明允許、同意"
        elif x1 == 0:
            msg = "笑筊：表示神明考慮中"
        else:
            msg = "陰筊：表示不宜"

        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }

    return render_template("cup.html", result=result)

# =========================
# Firestore
# =========================
@app.route("/read")
def read():
    result = ""
    docs = db.collection("靜宜資管").get()

    for doc in docs:
        data = doc.to_dict()
        result += f"姓名：{data.get('name','')}，研究室：{data.get('lab','')}<br>"

    return result + "<br><a href='/'>回首頁</a>"

@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip()
    result_html = ""

    if keyword:
        docs = db.collection("靜宜資管").get()

        for doc in docs:
            data = doc.to_dict()
            if keyword in str(data.get("name", "")):
                result_html += f"{data.get('name')} - {data.get('lab')}<br>"

        if result_html == "":
            result_html = "查無符合資料"

    return f"""
    <h2>老師查詢</h2>
    <form>
    <input name="keyword">
    <input type="submit" value="查詢">
    </form>
    {result_html}
    <br><a href="/">回首頁</a>
    """

# =========================
# 爬蟲
# =========================
@app.route("/spider1")
def spider1():
    url = "https://amy2005.vercel.app/about"
    data = requests.get(url)
    data.encoding = "utf-8"

    sp = BeautifulSoup(data.text, "html.parser")
    items = sp.select("td a")

    result = "<h2>爬蟲結果</h2>"

    for item in items:
        text = item.text.strip()
        href = item.get("href")
        result += f"{text} - {href}<br>"

    return result + "<br><a href='/'>回首頁</a>"

# =========================
# 即將上映電影（照你原本寫法）
# =========================
@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    data = requests.get(url)
    data.encoding = "utf-8"

    sp = BeautifulSoup(data.text, "html.parser")
    result = sp.select(".filmListAllX li")

    html = "<h1>即將上映電影</h1>"
    html += "<a href='/'>回首頁</a><br><br>"

    for item in result:
        name = item.find("img").get("alt")
        link = "http://www.atmovies.com.tw" + item.find("a").get("href")

        html += f"<a href='{link}' target='_blank'>{name}</a><br>"

    return html

# =========================
# 主程式
# =========================
if __name__ == "__main__":
    app.run(debug=True)
