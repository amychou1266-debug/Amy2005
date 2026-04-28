from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Firebase 初始化
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(BASE_DIR, "serviceAccountKey.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 爬蟲網址
url = "http://www.atmovies.com.tw/movie/next/"
Data = requests.get(url)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")
result = sp.select(".filmListAllX li")

info = ""

for item in result:
    img_tag = item.find("img")
    title_tag = item.find("div", class_="filmtitle")
    runtime_tag = item.find("div", class_="runtime")
    update_tag = item.find("div", class_="smaller09")

    if img_tag:
        picture = img_tag.get("src").replace(" ", "")
    else:
        picture = "無圖片"

    if title_tag:
        title = title_tag.text.strip()
        link_tag = title_tag.find("a")

        if link_tag:
            hyperlink = "http://www.atmovies.com.tw" + link_tag.get("href")
        else:
            hyperlink = "無連結"
    else:
        title = "無標題"
        hyperlink = "無連結"

    showDate = "無上映日期"
    showLength = "尚無片長資訊"

    if runtime_tag:
        show = runtime_tag.text.strip()

        if "上映日期：" in show:
            showDate = show.replace("上映日期：", "")[0:10]

        if "片長：" in show:
            showLength = show.split("片長：")[1].replace("分", "").replace(" ", "")

    if update_tag:
        lastUpdate = update_tag.text.strip()
    else:
        lastUpdate = "無更新日期"

    movie_id = title.replace("/", "").replace("\\", "").replace(" ", "")

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
    }

    db.collection("電影").document(movie_id).set(doc)

    info += picture + "\n"
    info += title + "\n"
    info += hyperlink + "\n"
    info += showDate + "\n"
    info += showLength + "\n"
    info += lastUpdate + "\n\n"

print(info)