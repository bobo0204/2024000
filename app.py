# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


import os
import sys
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import phonetic as ph

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def get_weather_info(city_name):
    # 模擬瀏覽器請求標頭
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # 目標URL
    base_url = 'https://www.cwa.gov.tw/V8/C/W/County/index.html'

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

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        message_text = event.message.text
        if message_text.startswith("天氣 "):  # 假設用戶發送 "天氣 城市名稱"
            city_name = message_text.split(" ", 1)[1]
            weather_info = get_weather_info(city_name)
            reply_text = weather_info
        else:
            reply_text = ph.read(message_text)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    return 'OK'

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
