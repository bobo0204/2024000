# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys
import random
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser
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

# Import custom math quiz function
from math_quiz import custom_math

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


def get_news():
    url = "https://travel.ettoday.net/category/%E6%A1%83%E5%9C%92/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = soup.find_all("h3", itemprop="headline", limit=5)
    news_titles = [title.text.strip() for title in titles]
    return "\n".join(news_titles)


def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        
        user_message = event.message.text
        if "新聞" in user_message:
            news = get_news()
            reply_text = news
        elif "題目" in user_message:
            expression, correct_answer = custom_math()
            reply_text = f"請計算：{expression}"
        else:
            try:
                user_answer = int(user_message.strip())
                if user_answer == correct_answer:
                    reply_text = "很棒，正確 ~"
                else:
                    reply_text = "錯誤，加油，再想想 ~"
            except ValueError:
                reply_text = "請輸入有效的整數答案。"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    return 'OK'


@app.route("/callback", methods=['POST'])
def webhook():
    return callback()


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', action='store_true', help='debug mode')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
