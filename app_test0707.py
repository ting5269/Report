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

line_bot_api = LineBotApi("dbhiwamQfucwWLjwPCp21vLiPGz69hdsJjv78eW8GzGzGY8j8Dp4ILcxNGeIuhrOeNUg+7rPCligcmdNdIqpo011ufMSTPTRFzs7Vp64uWKkSznojosbTrK4huo+EcDZ+nfNGZwptlVmb+YG6kXE3QdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("5789ff282b69b13e6131e9de1568480e")

@ app.route("/callback", methods=['POST'])
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
        with open("C:/Users/user/Desktop/LineBot/user_ids.txt", "r") as file:
            user_ids = set(file.read().splitlines())  # 讀取資料
        for user_id in user_ids:
            line_bot_api.push_message(user_id, message)
    except Exception as e:
        print(f"發送訊息時出現錯誤: {e}")

def schedule_jobs():
    # 設置每天特定時間發送消息
    schedule.every().day.at("16:49").do(send_scheduled_message)

@ handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_id = event.source.user_id  #獲取用戶的User ID
    print(f"User ID: {user_id}")  # print User ID 到控制台

    #將User ID儲存到文件中
    with open("C:/Users/user/Desktop/LineBot/user_ids.txt", "a") as file:
        file.write(user_id + "\n")


    if event.message.text == "a":
        msg = (TextSendMessage(text='這是測試'))
        line_bot_api.reply_message(event.reply_token, msg)
    elif event.message.text == '日報表顯示': #快速選單內容
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
    elif event.message.text == '周報表顯示': #快速選單內容
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
    elif event.message.text == '報表設定': #快速選單內容
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
    elif event.message.text =='日報表心率':
        msg3 = (TextSendMessage(text='心率測試'))
        line_bot_api.reply_message(event.reply_token, msg3)

    elif event.message.text =='日報表睡眠':
        {}
    elif event.message.text =='日報表活動':
        data = pd.read_csv('./Desktop/裡銳意程式碼/dailyActivity.csv')
        df = pd.DataFrame(data)
        #print(df)
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
        df.set_index('ActivityDate', inplace = True)
        specific_time = '2024-05-27'
        df_yesterday = df.loc[specific_time]
        #print(df_yesterday)

        # test = (TextSendMessage(text='失敗'))
        # line_bot_api.reply_message(event.reply_token, test)
        #抓久坐警示csv
        datawarning = pd.read_csv('./Desktop/裡銳意程式碼/warning.csv')
        df2 = pd.DataFrame(datawarning)
        df2['ActivityDate'] = pd.to_datetime(df2['ActivityDate'])
        
        df2.set_index('ActivityDate', inplace = True)
        df2_yesterday = df2.loc[specific_time]
        #print(df2_yesterday)
        #df2_yesterday.set_index('ActivityDate', inplace = True)
        StandUpAlert = df2_yesterday['StandUpAlert']
        #print(StandUpAlert)

        #將數據間隔整理為固定1小時                
        df_hourly = df_yesterday.resample('h').sum()
        #print(df_hourly)
        matplotlib.rc('font', family='Microsoft JhengHei')
        plt.figure(figsize=(10, 6))
        bars = plt.bar(df_hourly.index,df_hourly['Step'],width=0.03,align='center')
        #print(df_hourly['Step'])

        plt.xlabel('時間') 
        plt.ylabel('步數')

        #顯示總和步數
        total_steps = df_hourly['Step'].sum()
        plt.title(f'昨日活動 (總步數: {total_steps:.0f})')
        # 設置x軸刻度和標籤
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        hours = df_hourly.index
        plt.gca().set_xticks(hours)
        plt.gca().set_xticklabels([hour.strftime("%H:%M") for hour in hours])
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}', ha='center', va='bottom', fontsize=10)
            
        plt.tight_layout() 
        #圖表底下的講解
        summary_text1 = f'今日久坐提醒:{StandUpAlert}次'
        if(total_steps >= 8000):
            summary_text2 = '恭喜你！你已經達成了今日8000步的目標。繼續保持這種健康的生活方式，你的身體會感謝你的！'
        else:
            summary_text2 = f'還差{8000-total_steps}步就能達成目標8000步，繼續加油！'
        plt.figtext(0.07, 0.15, summary_text1 , ha='left', fontsize=12)
        plt.figtext(0.07, 0.1, summary_text2, ha='left', fontsize=12)
        plt.subplots_adjust(bottom=0.3)

        # output_path_activt_day="C:/Users/user/Desktop/image/report2.png"
        # plt.savefig(output_path_activt_day, bbox_inches='tight')
        plt.savefig('report2.png', bbox_inches='tight')
        PATH = 'report2.png'

        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title=plt.title)
        #儲存imgur連結
        activitydayimgurl = uploaded_image.link
    
        image_message = ImageSendMessage(
        original_content_url=activitydayimgurl,
        preview_image_url=activitydayimgurl
        )
        line_bot_api.reply_message(event.reply_token, image_message)
    elif event.message.text =="周報表活動":
        start_date = '2024-05-21'
        end_date = '2024-05-27'
        #mask = (df['ActivityDate'].dt.date >= pd.to_datetime(start_date).date() ) & (df['ActivityDate'].dt.date <= pd.to_datetime(end_date).date())
        df_week = df.loc[start_date:end_date]
        #print(df_week)
        #df_week.set_index('ActivityDate', inplace = True)

        #將數據間隔整理為固定1天
        df_daliy = df_week.resample('d').sum()
        #print(df_week)
        matplotlib.rc('font', family='Microsoft JhengHei')
        plt.figure(figsize=(10, 6))
        bars = plt.bar(df_daliy.index,df_daliy['Step'],width=0.8,align='center')
        #print(df_daliy['Step'])
        plt.title('上週活動量')
        plt.xlabel('日期')
        plt.ylabel('步數')
        plt.xticks(rotation=45)
        avgStep = int(np.average(df_daliy['Step']))
        plt.axhline(y=avgStep, color='r', linestyle='--',)
        plt.text(df_daliy.index[-1], avgStep, f' 平均值: {avgStep}', color='black', va='bottom', ha='left', fontsize = 12)

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}', ha='center', va='bottom', fontsize=10)
        #print(df_week['Step'])
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig('report2.png')
        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title=plt.title)
        #儲存imgur連結
        activityweekimgurl = uploaded_image.link
        image_message = ImageSendMessage(
        original_content_url=activityweekimgurl,
        preview_image_url=activityweekimgurl
        )
        line_bot_api.reply_message(event.reply_token, image_message)
        
    elif event.message.text =='日報表疲勞':
        {}
    elif event.message.text =='日報表全部':
        {}
    elif event.message.text == "早上8:00傳送報表":
        {}
    else : 
        msg2 = (TextSendMessage(text='失敗'))
        line_bot_api.reply_message(event.reply_token, msg2)


if __name__ == "__main__":
    schedule_jobs()
    port = int(os.environ.get('PORT', 5000))
    # 創建一個獨立的線程來運行定時任務
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    import threading
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()
    app.run(host='0.0.0.0', port=port)

