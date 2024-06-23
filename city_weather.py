# get_weather_info.py

import requests
from bs4 import BeautifulSoup

def get_weather_info(city_name):
    # 模擬瀏覽器請求標頭
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # 目標URL
    base_url = 'https://www.cwb.gov.tw/V8/C/W/County/County.html?CID='

    # 城市名稱和ID的映射
    city_ids = {
        "基隆市": "10017",
        "臺北市": "63",
        "新北市": "65",
        "桃園市": "68",
        "新竹市": "10018",
        "新竹縣": "10004",
        "苗栗縣": "10005",
        "臺中市": "66",
        "彰化縣": "10007",
        "南投縣": "10008",
        "雲林縣": "10009",
        "嘉義市": "10020",
        "嘉義縣": "10010",
        "臺南市": "67",
        "高雄市": "64",
        "屏東縣": "10013",
        "宜蘭縣": "10002",
        "花蓮縣": "10015",
        "臺東縣": "10014",
        "澎湖縣": "10016",
        "金門縣": "09020",
        "連江縣": "09007"
    }

    if city_name not in city_ids:
        return f"城市名稱 {city_name} 不在支持的範圍內。"

    # 拼接完整URL
    city_id = city_ids[city_name]
    full_url = base_url + city_id

    # 發送HTTP請求
    response = requests.get(full_url, headers=headers)
    
    if response.status_code != 200:
        return "無法訪問天氣信息網站。"

    # 解析HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # 查找並提取所需的天氣信息（這部分需根據實際網站結構進行調整）
    weather_info = soup.find('div', class_='current-briefing__content').get_text(strip=True)

    return weather_info
