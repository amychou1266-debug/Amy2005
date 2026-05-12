from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime
import random
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


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
    homepage += "<br><a href='/movie2'>movie2：讀取開眼電影並寫入Firestore</a><br>"
    homepage += "<a href='/movie3'>movie3：查詢電影資料</a><br>"
    homepage += "<a href='/road'>台中市十大肇事路口</a><br>"
    homepage += "<a href='/weather'>天氣查詢</a><br>"
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
# 即將上映電影
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

@app.route("/movie2")
def movie2():
    url = "http://www.atmovies.com.tw/movie/next/"
    data = requests.get(url)
    data.encoding = "utf-8"

    sp = BeautifulSoup(data.text, "html.parser")
    result = sp.select(".filmListAllX li")

    last_update_tag = sp.find("div", class_="smaller09")

    if last_update_tag:
        lastUpdate = last_update_tag.text[5:]
    else:
        lastUpdate = "無更新日期"

    for item in result:

        img_tag = item.find("img")
        title_tag = item.find("div", class_="filmtitle")
        runtime_tag = item.find("div", class_="runtime")

        # =========================
        # 電影分級
        # =========================
        level_img = item.select_one(".runtime img")

        if level_img:
            level = level_img.get("alt", "").strip()
        else:
            level = "未知"

        if not img_tag or not title_tag or not runtime_tag:
            continue

        a_tag = title_tag.find("a")

        if not a_tag:
            continue

        picture = img_tag.get("src", "").replace(" ", "")

        title = title_tag.text.strip()

        movie_id = a_tag.get("href")
        movie_id = movie_id.replace("/", "")
        movie_id = movie_id.replace("movie", "")

        hyperlink = "http://www.atmovies.com.tw" + a_tag.get("href")

        show = runtime_tag.text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")

        showDate = show[0:10]
        showLength = show[13:]

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "level": level,
            "lastUpdate": lastUpdate
        }

        db.collection("電影").document(movie_id).set(doc)

    return f"""
    <h1>電影資料更新完成</h1>
    更新日期：{lastUpdate}<br>
    <a href='/movie3'>前往電影查詢</a>
    """


@app.route("/movie3")
def movie3():

    keyword = request.args.get("keyword", "").strip()

    result = ""

    if keyword:

        docs = db.collection("電影").stream()

        for doc in docs:

            data = doc.to_dict()

            title = data.get("title", "")
            picture = data.get("picture", "")
            hyperlink = data.get("hyperlink", "")
            showDate = data.get("showDate", "")
            showLength = data.get("showLength", "")
            level = data.get("level", "")
            lastUpdate = data.get("lastUpdate", "")

            if keyword in title:

                result += f"""
                <div style='margin-bottom:30px;'>

                    <a href="{hyperlink}" target="_blank">
                        <h2>{title}</h2>
                    </a>

                    <img src="{picture}" width="200"><br><br>

                    電影分級：{level}<br>
                    上映日期：{showDate}<br>
                    電影片長：{showLength} 分鐘<br>
                    更新日期：{lastUpdate}<br>

                </div>

                <hr>
                """

        if result == "":
            result = "<h3>查無資料</h3>"

    return f"""
    <h1>即將上映電影查詢</h1>

    <form>

        請輸入電影名稱：

        <input type="text" name="keyword" value="{keyword}">

        <input type="submit" value="查詢">

    </form>

    <hr>

    {result}

    <br>

    <a href="/">回首頁</a>
    """
@app.route("/road")
def road():
    import json

    with open("臺中市113年10月份十大高肇事路口.JSON", "r", encoding="utf-8") as f:
        JsonData = json.load(f)

    result = "<h1>台中市十大肇事路口</h1>"

    for item in JsonData:
        result += f"""
        路口名稱：{item['路口名稱']}<br>
        總件數：{item['總件數']}<br>
        主要肇因：{item['主要肇因']}<br><br>
        """

    return result
    return result
@app.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "GET":
        return """
        <h1>天氣查詢</h1>
        <form method="post">
            請輸入縣市：
            <input name="city">
            <button type="submit">查詢</button>
        </form>
        """

    city = request.form["city"]

    # ⭐ 修正台 / 臺
    city = city.replace("台", "臺")

    # ⭐ 自動補「市」
    if not city.endswith("市"):
        city += "市"

    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": "rdec-key-123-45678-011121314",
        "format": "JSON",
        "locationName": city
    }

    Data = requests.get(url, params=params)
    JsonData = Data.json()

    locations = JsonData["records"]["location"]

    if len(locations) == 0:
        return f"""
        <h1>查無資料</h1>
        <p>你輸入的是：{city}</p>
        <p>請輸入完整縣市名稱，例如：臺中市、臺北市、高雄市</p>
        <a href="/weather">重新查詢</a>
        """

    location = locations[0]

    weather_now = location["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
    rain = location["weatherElement"][1]["time"][0]["parameter"]["parameterName"]

    return f"""
    <h1>{city}天氣查詢結果</h1>
    目前天氣：{weather_now}<br>
    降雨機率：{rain}%<br><br>
    <a href="/weather">重新查詢</a>
    """
@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    msg =  req.get("queryResult").get("queryText")
    info = "動作：" + action + "； 查詢內容：" + msg
    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/webhook3", methods=["POST"])
def webhook3():

    req = request.get_json(force=True)

    intent = req["queryResult"]["intent"]["displayName"]

    if intent == "Movie":

        name = req["queryResult"]["parameters"].get("name", "")
        level = req["queryResult"]["parameters"].get("rating", "")

        if "G" in level:
            level = "普遍級"
        elif "PG12" in level:
            level = "輔12級"
        elif "PG15" in level:
            level = "輔15級"
        elif "PG" in level:
            level = "保護級"
        elif "R" in level:
            level = "限制級"

        docs = db.collection("電影").get()

        result = ""

        for doc in docs:
            data = doc.to_dict()

            if level in data.get("level", ""):
                result += data.get("title", "") + "\n"

        if result == "":
            result = "查無符合電影"

        text = f"""
我是{周辰恩}
分級為：{level}
電影有：

{result}
"""

        return make_response(jsonify({
            "fulfillmentText": text
        }))

    return make_response(jsonify({
        "fulfillmentText": "找不到對應的 intent"
    }))

# =========================
# 主程式
# =========================
if __name__ == "__main__":
    app.run(debug=True)
