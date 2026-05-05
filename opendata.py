import requests

url = "https://datacenter.taichung.gov.tw/swagger/OpenData/34b9c2c7-8d2b-4a6f-9c0c-6b4f3e4b7f5d"

headers = {
    "User-Agent": "Mozilla/5.0"
}

Result = ""
Road = input("請輸入欲查詢的路名：")

try:
    Data = requests.get(url, headers=headers, timeout=10)
    Data.raise_for_status()

    JsonData = Data.json()

    for item in JsonData:
        road_name = item.get("路口名稱", "")
        count = str(item.get("總件數", 0))
        reason = item.get("主要肇因", "未知")

        if Road in road_name:
            Result += road_name + "：發生" + count + "件，主因是" + reason + "\n\n"

    if Result == "":
        Result = "抱歉，查無相關資料！"

    print(Result)

except Exception as e:
    print("錯誤：", e)