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

from linebot.models import TextSendMessage



CLIENT_ID = "122aba7e3e3f13a"
PATH = 'report2.png'

app = Flask(__name__)

line_bot_api = LineBotApi("A8ISwhsCwJuQrPe03vd+6xngj59R4nah0V4If0GKJjiSg4EIogYRCWzwE+0XA4Avkc2mBfZHLHCSQxWhkgmuykstCywsHIBXr1jn08CwQutNBrcrg5gzgIQIMDFF/LiYErXmttwdoHlegvBCRgRuYgdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("d969ac6229fcb01a73b29792667ec7b1")

# 用於存儲每個用戶的累積步數
user_steps = {}
# 勳章目標
milestones = [8000]
# 勳章圖片 URL
milestone_images = {
    8000: "https://i.imgur.com/4QfKuz1.png"
}

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

    global current_date, total_steps, days_counted

    user_input = event.message.text
    user_id = event.source.user_id  # 獲取用戶的User ID
    print(f"User ID: {user_id}")  # print User ID 到控制台
    matplotlib.rc('font', family='Microsoft JhengHei')

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

    elif user_input == "+1":
        # 獲取當前用戶的累積步數，如果沒有則初始化為0
        steps = user_steps.get(user_id, 0) + 1000
        user_steps[user_id] = steps
        
        # 計算距離目標步數的差距
        target_steps = 8000
        remaining_steps = max(target_steps - steps, 0)
        
        # 設定回覆消息
        if steps >= target_steps:
            reply_text = "恭喜達成目標！"
            # 發送對應勳章圖片
            image_url = milestone_images.get(target_steps, "")
            messages = [TextSendMessage(text=reply_text)]
            if image_url:
                messages.append(ImageSendMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                ))
        else:
            reply_text = f"目前步數: {steps} 步，距離目標 {target_steps} 步還有 {remaining_steps} 步。"
            messages = [TextSendMessage(text=reply_text)]

        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    elif user_input == "目前累積":
        # 獲取當前用戶的累積步數，如果沒有則初始化為0
        steps = user_steps.get(user_id, 0)
        remaining_steps = max(8000 - steps, 0)
        reply_text = f"目前累積步數: {steps} 步，距離 8000 步還有 {remaining_steps} 步。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    elif user_input == "重新計算":
        # 重置當前用戶的累積步數為0
        user_steps[user_id] = 0
        reply_text = "累積步數已歸零。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    elif event.message.text == '榮譽勳章': #快速選單內容
        message = TextSendMessage(
        text='請選擇一個選項',
        quick_reply=QuickReply(
           items=[
                QuickReplyButton(
                    action=MessageAction(label="今日成就", text="今日成就")
                ),
                QuickReplyButton(
                    action=MessageAction(label="目前進度", text="目前進度")
                ),
                QuickReplyButton(
                    action=MessageAction(label="+1天", text="+1")
                ),
                QuickReplyButton(
                    action=MessageAction(label="目前累積", text="目前累積")
                ),
                QuickReplyButton(
                    action=MessageAction(label="重新計算", text="重新計算")
                ),
            ]
        )
        )
        line_bot_api.reply_message(event.reply_token, message)
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

    
    

    elif event.message.text == '今日成就':
        try:
            # 讀取CSV文件
            data = pd.read_csv('./dailyActivity.csv')
            df = pd.DataFrame(data)
            
            # 將ActivityDate轉換為日期時間格式並設置為索引
            df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
            df.set_index('ActivityDate', inplace=True)
            
            # 選擇特定日期的數據
            specific_date = '2024-05-27'
            df_specific_date = df.loc[specific_date]
            
            # 計算當日總步數
            total_steps = df_specific_date['Step'].sum()
            
            # 判斷總步數是否超過10
            if total_steps > 10:
                reply_text = f'今日步數：{total_steps} 達標！你好棒！'
                image_url = 'https://i.imgur.com/4QfKuz1.png'
                
                # 發送文字消息
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text=reply_text),
                        ImageSendMessage(
                            original_content_url=image_url,
                            preview_image_url=image_url
                        )
                    ]
                )
            else:
                reply_text = f'今日步數：{total_steps} 未達標，加油哦！'
                
                # 發送文字消息
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_text)
                )
        except Exception as e:
            # 處理可能發生的錯誤
            error_message = f'處理數據時發生錯誤：{str(e)}'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_message)
            )

    

    elif event.message.text == '目前進度':
        try:
            # 讀取CSV文件
            data = pd.read_csv('./dailyActivity.csv')
            df = pd.DataFrame(data)
            
            # 將ActivityDate轉換為日期時間格式並設置為索引
            df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
            df.set_index('ActivityDate', inplace=True)
            
            # 獲取當月的第一天和今天的日期
            today = datetime.today()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            
            # 選擇日期範圍內的數據
            mask = (df.index >= start_date) & (df.index <= end_date)
            df_date_range = df.loc[mask]
            
            # 確認Step列存在
            if 'Step' not in df.columns:
                raise ValueError('Step列不存在於CSV文件中')
            
            # 計算日期範圍內的總步數
            total_steps = df_date_range['Step'].sum()
            
            # 發送進度消息
            reply_text = f'從 {start_date} 到 {end_date}，你的總步數是：{total_steps} 步。'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
        
        except Exception as e:
            # 處理其他可能發生的錯誤
            error_message = f'處理數據時發生錯誤：{str(e)}'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_message)
            )


    
    elif event.message.text == '日報表活動':
        data = pd.read_csv('./dailyActivity.csv')
        df = pd.DataFrame(data)
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
        df.set_index('ActivityDate', inplace=True)
        specific_time = '2024-05-27'
        df_yesterday = df.loc[specific_time]

        datawarning = pd.read_csv(./warning.csv')
        df2 = pd.DataFrame(datawarning)
        df2['ActivityDate'] = pd.to_datetime(df2['ActivityDate'])
        df2.set_index('ActivityDate', inplace=True)
        df2_yesterday = df2.loc[specific_time]
        StandUpAlert = df2_yesterday['StandUpAlert']

        df_hourly = df_yesterday.resample('h').sum()
        
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
