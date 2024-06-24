from flask import Flask, request, abort
from linebot import LineBotApi, WebhookParser, exceptions
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import sys
import requests
from bs4 import BeautifulSoup
from math_quiz import generate_question, check_answer  # 修改 import 語句

app = Flask(__name__)

# 略過 channel_secret 和 channel_access_token 部分

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def get_news():
    url = "https://travel.ettoday.net/category/%E6%A1%83%E5%9C%92/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = soup.find_all("h3", itemprop="headline", limit=5)
    news_titles = [title.text.strip() for title in titles]
    return "\n".join(news_titles)

@app.route("/callback", methods=['POST'])
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
            # 調用 generate_question 函式來生成數學題目
            expression, correct_answer = generate_question()
            reply_text = f"請計算：{expression}"
        else:
            reply_text = "抱歉，我不太明白你的意思。"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    return 'OK'

if __name__ == "__main__":
    app.run(debug=True)
