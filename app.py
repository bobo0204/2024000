# -*- coding: utf-8 -*-

import os
import sys
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
import random

app = Flask(__name__)

# 從環境變數中讀取 LINE Bot 的 channel secret 和 channel access token
line_channel_secret = os.getenv('LINE_CHANNEL_SECRET')
line_channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if line_channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if line_channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(line_channel_access_token)
parser = WebhookParser(line_channel_secret)

def generate_question():
    while True:
        # Generate three random single-digit numbers
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        num3 = random.randint(1, 9)
        
        # Randomly choose two operators
        operators = ['+', '-', '*', '/']
        operator1 = random.choice(operators)
        operator2 = random.choice(operators)

        # Construct the mathematical expression
        expression = f"{num1} {operator1} {num2} {operator2} {num3}"
        
        # Calculate the correct answer
        try:
            correct_answer = eval(expression)
            # Check if the answer is an integer with no remainder
            if correct_answer == int(correct_answer):
                return expression, int(correct_answer)
        except ZeroDivisionError:
            continue
        except SyntaxError:
            continue

def ask_question():
    # Generate a random question
    expression, correct_answer = generate_question()
    
    # Prompt user to calculate the expression
    prompt = f"Please calculate: {expression}"
    
    return prompt, correct_answer

def check_answer(user_answer, correct_answer):
    try:
        user_answer = int(user_answer)
    except ValueError:
        return "Please enter a valid integer answer."
    
    if user_answer == correct_answer:
        return "Great job, correct!"
    else:
        return "Incorrect, keep trying!"

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
        if "news" in user_message.lower():
            news = get_news()
            reply_text = news
        elif "question" in user_message.lower():
            expression, correct_answer = generate_question()
            reply_text = f"Please calculate: {expression}"
        else:
            reply_text = "Sorry, I don't understand."

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
