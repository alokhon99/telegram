import requests, re
from time import sleep
from bs4 import BeautifulSoup
import requests
import pytz
import datetime
import os
import psycopg2
from dbhelper import DBHelper
from telegram import Update
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler

db = DBHelper()
button_help = 'Помощь'

url = "https://api.telegram.org/bot1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8/"
url_t = "https://www.sports.ru/"

RU_MONTH_VALUES = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}

class Team:
    def __init__(self, name):
        print('init')
        self.name = name
        self.upd()
        
    def upd(self):
        print('upd')
        global url_t;
        html_content = requests.get(url_t + self.name + '/').text
        soup = BeautifulSoup(html_content, "lxml")
        contents=soup.find_all('div', class_='commands')
        next_match = contents[1]
        self.team1 = next_match.find_all('span')[1].text
        self.team2 = next_match.find_all('span')[3].text
        details = soup.find_all('div', class_='score-descr')[1]
        dt_full = details.text
        dt_full = dt_full.replace(next_match.text,'')
        dt_words = dt_full.split(' ')
        self.date = dt_words[0].lstrip() + ' ' + dt_words[1]
        time = dt_words[2]
        self.tournament = ''
        for w in dt_words[3:]:
            self.tournament = self.tournament + w + ' '
        self.tournament = self.tournament.replace('|\n', '').lstrip()
        temp = time.split(':')
        hour = int(temp[0])
        hour = hour + 2
        if hour > 23:
            hour = hour - 24
        self.hour = str(hour)
        self.minute = temp[1]
        
    def get_message(self):
        print(self.is_passed())
        return 'Следующий матч: ' + '\n' + self.tournament + self.date+ ' ' + self.hour+':'+self.minute + '\n' +  self.team1 + ' - ' + self.team2
    
    def is_passed(self):
        dt = self.date.split(' ')
        day = str(int(dt[0]))
        mon = int_value_from_ru_month(dt[1])
        date = datetime.datetime.strptime(day+'/'+mon+'/2020', "%d/%m/%Y").date()
        today = date.today()
        if today > date:
            return True
        elif today == date and self.hour > 12:
            tz = pytz.timezone('Asia/Tashkent')
            now = datetime.datetime.now(tz)
            print(now)
            my_time_string = self.hour+':'+self.minute+':'+'00'
            my_datetime = datetime.datetime.strptime(my_time_string, "%H:%M:%S")
            my_datetime = now.replace(hour=my_datetime.time().hour, minute=my_datetime.time().minute, second=my_datetime.time().second, microsecond=0)
            if (now > my_datetime):
                return True
        else:
            return False
        
    name = 'team'
    team1 = 'team'
    team2 = 'opponent'
    hour = '00'
    minute = '00'
    date = '12'
    tounament = 'epl'
    
team1 = Team('liverpool')
team2 = Team('arsenal')
team3 = Team('chelsea')
team4 = Team('real')
team5 = Team('barcelona')
team6 = Team('mu')
team7 = Team('juventus')
team8 = Team('manchester-city')

def int_value_from_ru_month(date_str):
    for k, v in RU_MONTH_VALUES.items():
        date_str = date_str.replace(k, str(v))
    return date_str

def get_updates_json(request, offset=None):
    print('get_update_e')
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(request + 'getUpdates', data=params)
    print('get_update_o')
    return response.json()


def last_update(data):  
    results = data['result']
    if len(results) == 0:
        return
    total_updates = len(results) - 1
    return results[total_updates]

def get_chat_id(update):  
    chat_id = update['message']['chat']['id']
    return chat_id

def send_mess(chat, text):  
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params)
    return response

def get_mess(update):
    message = update['message']['text']
#     author = update['message']['chat']['first_name']
    return message;

def action(message, chat):
     global team1 
     global team2 
     global team3 
     global team4 
     global team5 
     global team6
     global team7 
     global team8 
     if message == 'liverpool' or message == '/liverpool':
         if team1.is_passed():
            team1.upd()
         send_mess(chat, team1.get_message())
     elif message == 'arsenal' or message == '/arsenal':
         if team2.is_passed():
            team2.upd()
         send_mess(chat, team2.get_message())
     elif message == 'chelsea' or message == '/chelsea':
         if team3.is_passed():
            team3.upd()
         send_mess(chat, team3.get_message())
     elif message == 'real' or message == '/real':
         if team4.is_passed():
            team4.upd()
         send_mess(chat, team4.get_message())
     elif message == 'barcelona' or message == '/barcelona' or message == 'barsa':
         if team5.is_passed():
            team5.upd()
         send_mess(chat, team5.get_message())
     elif message == 'mu' or message == '/mu' or message == 'mu':
         if team6.is_passed():
            team6.upd()
         send_mess(chat, team6.get_message())
     elif message == 'juventus' or message == '/juventus' or message == 'juve' or message == 'cr7' or message == 'penaldu':
         if team7.is_passed():
            team7.upd()
         send_mess(chat, team7.get_message())
     elif message == 'manchester-city' or message == '/city' or message == 'city' or message == 'bir qop pul' or message == 'kalbosh' or message == 'kal':
         if team8.is_passed():
            team8.upd()
         send_mess(chat, team8.get_message())
     elif message == '/fav':
         db.add_item('1')
         items = db.get_items()
         send_mess(chat, items)
     else:
         send_mess( chat,'Используйте команды начинающиеся с /')

def button_country_handler(update: Update, context: CallbackContext):
    message = update.message.text
    if message == 'Angliya':
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Liverpool')
                    ],
                [
                    KeyboardButton(text='Arsenal')
                    ],
                [
                    KeyboardButton(text='Chelsea')
                    ],
                [
                    KeyboardButton(text='Manchester United')
                    ],
                [
                    KeyboardButton(text='Manchester City')
                    ],
                [
                    KeyboardButton(text='Turnir jadvali')
                    ],
            ],
            resize_keyboard=True,)
    elif message == 'Ispaniya':
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Barcelona')
                    ],
                [
                    KeyboardButton(text='Real Madrid')
                    ],
            ],
            resize_keyboard=True,)
    elif message == 'Italia':
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Juventus')
                    ],
                [
                    KeyboardButton(text='Milan')
                    ],
            ],
            resize_keyboard=True,)
        
    update.message.reply_text(
        text=message+' jamoasini tanlang',
        reply_markup=reply_markup,
    )
def message_handler(update: Update, context: CallbackContext):
    message = update.message.text

    if message == 'Angliya' or message == 'Ispaniya' or message == 'Italiya':
        return button_country_handler(update=update, context=context)
    else:
        text = 'Davlatni tanglang'
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Angliya')
                    ],
                [
                    KeyboardButton(text='Ispaniya')
                        ],
                [
                    KeyboardButton(text='Italiya')
                        ],
            ],
            resize_keyboard=True,)
        
    update.message.reply_text(
        text= text
        reply_markup=reply_markup,
    )

def main():
    db.setup()
    updater = Updater(
        token = '1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8',
        use_context=True,
    )
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=message_handler))
    updater.start_polling()
    updater.idle()

#     while(1):
#         json = last_update(get_updates_json(url))
#         if json != None:
#             break
#     update_id = json['update_id']
#     while True:
#         print("loop")
#         json = last_update(get_updates_json(url,update_id))
#         if json == None:
#               continue
#         delay = update_id - json['update_id']
#         print(delay)
#         if delay == 0:
# #             message = re.sub(r'men\b','man', message)
# #             message = re.sub(r'sen\b','san', message)
# #             message = re.sub(r'iq\b','u', message)
# #             message = re.sub(r'men\b','man', message)
# #             message = re.sub(r'mayman\b','miman', message)
# #             message = re.sub(r'maysan\b','misan', message)
# #             message = re.sub(r'yab','vo', message)
#             message = get_mess(json)
#             message = message.lower()
#             chat = get_chat_id(json)
#             action(message, chat)
#             update_id += 1
#         elif delay < 0:
#             bigJ = get_updates_json(url)
#             results = bigJ['result']
#             if len(results) == 0:
#                 return
#             total_updates = len(results) - 1
#             prev = results[total_updates + delay]
#             message = get_mess(prev)
#             message = message.lower()
#             chat = get_chat_id(prev)
#             action(message, chat)
#             update_id += 1
#         sleep(1)       

if __name__ == '__main__':  
    main()
