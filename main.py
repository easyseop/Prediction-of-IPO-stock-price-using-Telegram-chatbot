import telegram
from telegram.ext import Updater,MessageHandler,Filters,CommandHandler
import emoji
import os
from telegram_bot.config import api_key,chat_id
from database.stock import StockModel
from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO


bot = telegram.Bot(token = api_key)
BASE_PATH  = os.getcwd()

info_message = '''다음의 명령어를 입력해주세요.

- 안부 물어보기 : 뭐해
- 공모주 가격 물어보기 : 공모주 + "기업명"
- 차트 보기 : "기업명" + 차트
- 사진 보기 : 사진
'''
client = MongoClient('localhost', 27017)
db = client['Ipo']

def start(update, context):
    bot.sendMessage(chat_id = chat_id,text='안녕하세요 IPO 공모가 예측 봇 Stock-Manager 입니다.') # 채팅방에 입장했을 때, 인사말 
    bot.sendMessage(chat_id=update.effective_chat.id, text=info_message)


# bot.sendMessage(chat_id = chat_id,text=info_message)

# updater
updater = Updater(token=api_key, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling() # 주기적으로 텔레그램 서버에 접속해서 chatbot으로부터 새로운 메세지가 존재하면 받아오는 명령어.


def get_graph(cor_name,cor_shape):
    
    plt.clf()
    df = pd.DataFrame(db.inform.find({},{'_id':False}))	# 모든 데이터 조회
    df=df.dropna()
    
    
    df=df.sort_values(by=[cor_shape])
        
    plt.rcParams["font.family"] = "NanumGothic"
    line= plt.plot(df['기업명'],df[cor_shape],color='b') 
    plt.setp(line, color='black', linewidth=3.0)
    ax = plt.gca()
        
    plt.xticks(df['기업명'], df['기업명'], rotation=90)
    

    x= db.inform.find_one({'기업명': cor_name})['기업명']
    y= db.inform.find_one({'기업명': cor_name})[cor_shape]
        
    plt.scatter(x,y,color='r',s=250,label=cor_name) 
        
    plt.style.use('ggplot')
    plt.legend(loc="upper right")
    plt.title(cor_name +"  "+ cor_shape)
    ax.axes.xaxis.set_visible(False)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
        
    return buf
    
def handler(update, context):
    user_text = update.message.text # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.

    if '뭐해' in user_text: 
        bot.send_message(chat_id=update.effective_chat.id, text="챗봇에 대해 공부하는 중이에요.") # 답장 보내기
    elif '공모주'in user_text: 
        cor_name = user_text.split()[1]

        if  db.inform.find_one({'기업명': cor_name}):
            price = db.inform.find_one({'기업명': cor_name})['시초가']
            bot.send_message(chat_id=update.effective_chat.id, text=f"{cor_name} 주식의 시초가는 {price}원 입니다.") # 답장 보내기
        else:
            bot.send_message(chat_id=update.effective_chat.id, text="수집되지 않은 정보입니다.") # 답장 보내기
            
    elif '차트종류' in user_text:
       bot.send_message(chat_id=update.effective_chat.id, text=f"1.경쟁률\n2.의무보유확약\n3.청약경쟁률\n4.확정공모가\n")
                  
    elif '차트' in user_text:
        cor_name = user_text.split()[1]
        cor_shape = user_text.split()[2]
        bot.send_message(chat_id=update.effective_chat.id, text=f"{cor_name}주식의 차트를 불러오는 중입니다!")
        
        buf = get_graph(cor_name,cor_shape)
        bot.send_photo(chat_id =update.effective_chat.id,photo=buf)
        

    elif '사진' in user_text:
        bot.send_photo(chat_id = update.effective_chat.id, photo=open(BASE_PATH+'/telegram_bot/test_chart.jpeg','rb')) #

    elif '크롤링' in user_text:
        cor_name = user_text.split()[1]
        bot.send_photo(chat_id = update.effective_chat.id, photo=open(BASE_PATH+'/telegram_bot/test_chart.jpeg','rb')) #

start_handler = CommandHandler('start',start)
echo_handler = MessageHandler(Filters.text,handler) # chatbot에게 메세지를 전송하면,updater를 통해 필터링된 text가 handler로 전달이 된다. -> 가장 중요하고, 계속해서 수정할 부분


dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)



