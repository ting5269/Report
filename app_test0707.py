import os
from linebot.api import LineBotApiError
import numpy as np
from datetime import datetime, timedelta
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import pyimgur
import time
import schedule 

CLIENT_ID = "122aba7e3e3f13a"
PATH = 'report2.png'

app = Flask(__name__)

line_bot_api = LineBotApi("hQJcvO4Qf+QCC1DmH8LHbrKdmrd149Ry1v1xJ69jkf+O3+U6KHDVR3g6bjkGOLuURZkLXZoRojA+wtuEVNM841yVzpNVZfwrOufakv10iBSgzRiL8ZHllBQkNICYd6HumClRBbR/sG10oreTRLVERgdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("93e61e04ad5a8cac33ef67eac0f8e4e5")

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def send_scheduled_message():
    try:
        message = TextSendMessage(text="這是一條定時訊息")
        with open("./user_ids.txt", "r") as file:
            user_ids = set(file.read().splitlines())  # 讀取資料
        for user_id in user_ids:
            line_bot_api.push_message(user_id, message)
    except Exception as e:
        print(f"發送訊息時出現錯誤: {e}")

def schedule_jobs():
    # 設置每天特定時間發送消息
    schedule.every().day.at("23:50").do(send_scheduled_message)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    user_id = event.source.user_id  # 獲取用戶的User ID
    print(f"User ID: {user_id}")  # print User ID 到控制台

    # 將User ID儲存到文件中
    with open("./user_ids.txt", "a") as file:
        file.write(user_id + "\n")

    if event.message.text == "a":
        msg = TextSendMessage(text='這是測試')
        line_bot_api.reply_message(event.reply_token, msg)
    elif user_input == "1":
        reply_text = "你好"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    elif event.message.text == '日報表顯示':  # 快速選單內容
        message = TextSendMessage(
            text='請選擇一個選項',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="心率", text="日報表心率")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="睡眠", text="日報表睡眠")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="活動", text="日報表活動")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="疲勞", text="日報表疲勞")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="全部", text="日報表全部")
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == '周報表顯示':  # 快速選單內容
        message = TextSendMessage(
            text='請選擇一個選項',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="心率", text="周報表心率")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="睡眠", text="周報表睡眠")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="活動", text="周報表活動")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="疲勞", text="周報表疲勞")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="全部", text="周報表全部")
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == '報表設定':  # 快速選單內容
        message = TextSendMessage(
            text='請選擇一個選項',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="早上8:00傳送報表", text="早上8:00傳送報表")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="中午12:00傳送報表", text="中午12:00傳送報表")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="下午16:00傳送報表", text="下午16:00傳送報表")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="晚上20:00傳送報表", text="晚上20:00傳送報表")
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == '日報表心率':
        msg3 = TextSendMessage(text='心率測試')
        line_bot_api.reply_message(event.reply_token, msg3)
    elif event.message.text == '日報表睡眠':
        {}
    elif event.message.text == '日報表活動':
        data = pd.read_csv('./dailyActivity.csv')
        df = pd.DataFrame(data)
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
        df.set_index('ActivityDate', inplace=True)
        specific_time = '2024-05-27'
        df_yesterday = df.loc[specific_time]

        datawarning = pd.read_csv('./warning.csv')
        df2 = pd.DataFrame(datawarning)
        df2['ActivityDate'] = pd.to_datetime(df2['ActivityDate'])
        df2.set_index('ActivityDate', inplace=True)
        df2_yesterday = df2.loc[specific_time]
        StandUpAlert = df2_yesterday['StandUpAlert']

        df_hourly = df_yesterday.resample('h').sum()
        matplotlib.rc('font', family='Microsoft JhengHei')
        plt.figure(figsize=(10, 6))
        bars = plt.bar(df_hourly.index, df_hourly['Step'], width=0.03, align='center')

        plt.xlabel('時間')
        plt.ylabel('步數')

        total_steps = df_hourly['Step'].sum()
        plt.title(f'昨日活動 (總步數: {total_steps:.0f})')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        hours = df_hourly.index
        plt.gca().set_xticks(hours)
        plt.gca().set_xticklabels([hour.strftime("%H:%M") for hour in hours])
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}', ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        summary_text1 = f'今日久坐提醒:{StandUpAlert}次'
        if total_steps >= 8000:
            summary_text2 = '恭喜你！你已經達成了今日8000步的目標。繼續保持這種健康的生活方式，你的身體會感謝你的！'
        else:
            summary_text2 = f'還差{8000-total_steps}步就能達成目標8000步，繼續加油！'
        plt.figtext(0.07, 0.15, summary_text1, ha='left', fontsize=12)
        plt.figtext(0.07, 0.1, summary_text2, ha='left', fontsize=12)
        plt.subplots_adjust(bottom=0.3)

        plt.savefig('report2.png', bbox_inches='tight')
        PATH = 'report2.png'

        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title=plt.title)
        activitydayimgurl = uploaded_image.link

        image_message = ImageSendMessage(
            original_content_url=activitydayimgurl,
            preview_image_url=activitydayimgurl
        )
        line_bot_api.reply_message(event.reply_token, image_message)
    elif event.message.text == '周報表活動':
        start_date = '2024-05-21'
        end_date = '2024-05-27'
        mask = (df.index >= start_date) & (df.index <= end_date)
        df_week = df.loc[mask]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(df_week.index, df_week['Step'], width=0.5, align='center')

        plt.xlabel('日期')
        plt.ylabel('步數')
        total_steps = df_week['Step'].sum()
        plt.title(f'周活動 (總步數: {total_steps:.0f})')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        days = df_week.index
        plt.gca().set_xticks(days)
        plt.gca().set_xticklabels([day.strftime("%m-%d") for day in days])
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}', ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig('report2.png', bbox_inches='tight')
        PATH = 'report2.png'

        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title=plt.title)
        activityweekimgurl = uploaded_image.link

        image_message = ImageSendMessage(
            original_content_url=activityweekimgurl,
            preview_image_url=activityweekimgurl
        )
        line_bot_api.reply_message(event.reply_token, image_message)

if __name__ == "__main__":
    schedule_jobs()
    app.run(debug=True)
