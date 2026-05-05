import requests
import json

url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName=臺中市"

Data = requests.get(url)

# 只解析一次
JsonData = json.loads(Data.text)

# 天氣資料描述
WeatherTitle = JsonData["records"]["datasetDescription"]
print(WeatherTitle)

# 地區資料
Weather = JsonData["records"]["location"][0]
print(Weather)

# 天氣狀況 + 降雨機率
Wx = JsonData["records"]["location"][0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
Rain = JsonData["records"]["location"][0]["weatherElement"][1]["time"][0]["parameter"]["parameterName"]

print(Wx + "，降雨機率：" + Rain + "%")