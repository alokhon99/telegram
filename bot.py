import requests, re
import telegram.ext
from time import sleep
from bs4 import BeautifulSoup
import requests
import pytz
import datetime
from datetime import datetime
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

DATABASE_URL = os.environ['DATABASE_URL']

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


class Match:
    def __init__(self, which, url):
        self.which = which
        if which == 'p':
            self.update_as_prev(url)
        elif which == 'n':
            self.update_as_next(url)
        
    def update_as_next(self, name):
        print('upd next')
        global url_t;
        html_content = requests.get(url_t + name + '/').text
        soup = BeautifulSoup(html_content, "lxml")
        contents=soup.find_all('div', class_='commands')
        next_match = contents[1]
        self.team1 = next_match.find_all('span')[1].text
        self.team2 = next_match.find_all('span')[3].text
        print('upd next'+self.team1+self.team2)
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
        self.score = '_:_'
        print('upd next tugadi')
    
    def update_as_prev(self, name):
        print('upd prev')
        global url_t;
        html_content = requests.get(url_t + name + '/').text
        soup = BeautifulSoup(html_content, "lxml")
        contents=soup.find_all('div', class_='commands')
        next_match = contents[0]
        self.team1 = next_match.find_all('a')[0].text
        self.team2 = next_match.find_all('a')[1].text
        details = soup.find_all('div', class_='score-descr')[0]
        dt_full = details.text
        dt_full = dt_full.replace(next_match.text,'')
        dt_words = dt_full.split(' ')
        print(dt_words)
        self.date = dt_words[0].lstrip() + ' ' + dt_words[1]
        time = dt_words[2]
        print(time)
        self.tournament = ''
        for w in dt_words[3:]:
            if 'завершен' in w:
                break    
            self.tournament = self.tournament + w + ' '
        self.tournament = self.tournament.replace('|', '').lstrip()
        temp = time.split(':')
        hour = int(temp[0])
        hour = hour + 2
        if hour > 23:
            hour = hour - 24
        self.hour = str(hour)
        self.minute = temp[1]
        con = soup.find_all('div', class_='score score-red')
        if len(con) == 0:
            con = soup.find_all('div', class_='score score-green')
            if len(con) == 0:
                con = soup.find_all('div', class_='score score-orange')
        our_class = con[0]
        number1 = our_class.find_all('span')[0].text.rstrip().lstrip()
        number2 = our_class.find_all('span')[1].text.lstrip().rstrip()
        self.score = number1 + ' : ' + number2
        print('upd prev tugadi')
        
    
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
        
    def get_message(self):
        if self.which == 'p':
            return 'Последный матч: ' + '\n' + self.tournament + self.date+ ' ' + self.hour+':'+self.minute + '\n' +  self.team1 + ' '+self.score+' '+ self.team2
        return 'Следующий матч: ' + '\n' + self.tournament + self.date+ ' ' + self.hour+':'+self.minute + '\n' +  self.team1 + ' - '+ self.team2    
     
        
    team1 = 'team'
    team2 = 'opponent'
    hour = '00'
    minute = '00'
    date = '12'
    tounament = 'epl'
    which = '0'
    score = '_:_'
       

class Team:
    
    def __init__(self, name):
        print('init')
        self.name = name
        p = Match('p', name)
        n = Match('n', name)
        self.next = n
        self.prev = p
        
    def get(self, message):
        if self.next.is_passed():
            self.next.update_as_next()
            self.prev.update_as_prev()
        if message == "Keyingi o'yin":
            return self.next.get_message()
        else:
            return self.prev.get_message()
        
    
    def get_prev(self):
        if self.next.is_passed():
            self.next.update_as_next()
            self.prev.update_as_prev()
        return self.prev.get_message()
    
    
class User:
    
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def get_commands(self):
        return self.commands

    def add_commands(self,command):
        print('add_commands')
        self.commands.append(command)
        
    def get_last_command(self):
        return self.commands[len(self.commands)-2]
    
    def clear_history(self):
        self.commands = []
        
    def get_back(self):
        if self.state == 2:
            return self.league
        else:
            return 'any'

    chat_id = 0
    team = ' '
    league = ' '
    state = 0
    commands = []    
    
    
team1 = Team('liverpool')
team2 = Team('arsenal')
team3 = Team('chelsea')
team4 = Team('real')
team5 = Team('barcelona')
team6 = Team('mu')
team7 = Team('juventus')
team8 = Team('manchester-city')
team9 = Team('milan')
users = []

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

def create_tables():
    global DATABASE_URL
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username VARCHAR(255),
            fav VARCHAR(20)
            
            
        )
        """,
        """ CREATE TABLE IF NOT EXISTS teams(
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
                )
        """)
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print(conn)
        print('connection set')
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
            print('command executed')
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
def users_db():
    global DATABASE_URL
    sql = """SELECT * FROM users;"""
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print('connect set user_db')
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql)
        print('executed')
        # get the generated id back
        users = cur.fetchall() 
        print(users)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            
def insert_user(chat_id):
    print('insert')
    global DATABASE_URL
    sql = """INSERT INTO users(chat_id)
             VALUES(%s) RETURNING chat_id;"""
    print('insert')
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print('connect set')
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        chat_id = str(chat_id)
        print(chat_id)
        cur.execute(sql, (chat_id,))
        print('executed')
        # get the generated id back
        chat_id = cur.fetchone()
        print(chat_id)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            
def insert_fav(chat_id, fav):
    print('insert')
    global DATABASE_URL
    sql = """UPDATE users
             SET fav = %s
             WHERE chat_id = %s;"""
    print('update')
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print('connect set')
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql,(fav, chat_id))
        print('executed')
        # get the generated id back
        chat_id = cur.fetchone()[0]
        print(chat_id)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return chat_id

def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')

def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return
 
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))
 
        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)
 
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')
def get_user(chat_id):
    print('select')
    global DATABASE_URL
    sql = """SELECT fav FROM users
             WHERE chat_id = %s;"""
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print('connect set')
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        chat_id = str(chat_id)
        cur.execute(sql, (chat_id,))
        print('executed')
        # get the generated id back
        fav = cur.fetchone()
        if fav != None:
            fav = fav[0]
        print(fav)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return fav

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

def button_country_handler(update: Update, context: CallbackContext, message):
    print("handlerga keldi")
    print("bu "+message+" message")
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
                [KeyboardButton(text='Orqaga')],
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
                [KeyboardButton(text='Orqaga')],
            ],
            resize_keyboard=True,)
    elif message == 'Italiya':
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Juventus')
                    ],
                [
                    KeyboardButton(text='Milan')
                    ],
                [KeyboardButton(text='Orqaga')],
            ],
            resize_keyboard=True,)
        
    update.message.reply_text(
        text=message+' jamoasini tanlang',
        reply_markup=reply_markup,
    )
    
def button_team_handler(update: Update, context: CallbackContext):
    print("team handler")
    reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
    update.message.reply_text(
        text="Izlayotgan ma'lumotingizni tanlang",
        reply_markup=reply_markup,
    )
    
def message_handler(update: Update, context: CallbackContext):
    message = update.message.text
    print(update.message.chat_id)
    type(update.message.chat_id)
    global users
    x = None
    for u in users:
        if u.chat_id == update.message.chat_id:
            x = u
            break
    if x == None:
        fav = get_user(update.message.chat_id)
        print(fav)
        if fav == None:
            print("if")
            insert_user(update.message.chat_id)
        x = User(update.message.chat_id)
        x.fav = fav
        users.append(x)
    users_db()
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
                [
                    KeyboardButton(text='Sevimli Jamoa')
                        ],
            ],
            resize_keyboard=True,)
    if message == 'Sevimli Jamoa':
        update.message.reply_text(
                text= x.fav,
                reply_markup=reply_markup,)
        return
    elif message == "Kuzatib borish":
        insert_fav(x.chat_id, x.team)
        x.fav = x.team
        reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        update.message.reply_text(
                text= x.team + " jamoasi Sevimlilar bo'limiga tushdi",
                reply_markup=reply_markup,)
        return
    elif message == "Orqaga":
        message = x.get_back()
        print(message)
    if message == 'Angliya' or message == 'Ispaniya' or message == 'Italiya':
        print("keldi buyoga")
        x.league = message
        x.state = 1
        return button_country_handler(update=update, context=context, message=message)
    elif message == 'Liverpool' or message == 'Arsenal' or message == 'Chelsea' or message == 'Real Madrid' or message == 'Barcelona' or message == 'Manchester United' or message == 'Juventus' or message == 'Manchester City' or message == 'Milan':
        x.team = message
        x.state = 2
        return button_team_handler(update=update, context=context)
    elif message == "Keyingi o'yin" or message =="So'nggi o'yin":
        m = message
        message = x.team
        reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        if message == 'Liverpool' or message == '/liverpool':
            update.message.reply_text(
                 text= team1.get(m),
                reply_markup=reply_markup,
            )
        elif message == 'Arsenal' or message == '/arsenal':
            update.message.reply_text(
                 text= team2.get(m),
                reply_markup=reply_markup,
            )
        elif message == 'Chelsea' or message == '/chelsea':
            update.message.reply_text(
                 text= team3.get(m),
                reply_markup=reply_markup,
            )
        elif message == 'Real Madrid' or message == '/real':
            update.message.reply_text(
                 text= team4.get(m),
                reply_markup=reply_markup,
            )
        elif message == 'Barcelona' or message == '/barcelona' or message == 'barsa':
            update.message.reply_text(
             text= team5.get(m),
             reply_markup=reply_markup,
            )
        elif message == 'Manchester United' or message == '/mu' or message == 'mu':
            update.message.reply_text(text= team6.get(m),reply_markup=reply_markup,)
        elif message == 'Juventus' or message == '/juventus' or message == 'juve' or message == 'cr7' or message == 'penaldu':
            update.message.reply_text(
                 text= team7.get(m),
                 reply_markup=reply_markup,
            )
        elif message == 'Manchester City' or message == '/city' or message == 'city' or message == 'bir qop pul' or message == 'kalbosh' or message == 'kal':
            update.message.reply_text(
                 text= team8.get(m),
              reply_markup=reply_markup,
             )
        elif message == 'Milan':
            update.message.reply_text(
                 text= team9.get(m),
                 reply_markup=reply_markup,
            )  
        print('keldi')
    elif message == 'Turnir jadvali':
        
        text = ''
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Orqaga')
                    ],
            ],
            resize_keyboard=True,)
        print('+')
        update.message.reply_text(
           text= text,
            reply_markup=reply_markup,
        )
    else:
        x.clear_history()
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
                [
                    KeyboardButton(text='Sevimli Jamoa')
                        ],
            ],
            resize_keyboard=True,)
        print('+')
        update.message.reply_text(
           text= text,
            reply_markup=reply_markup,
        )
def callback_30(context: telegram.ext.CallbackContext):
    print(context)
    context.bot.send_message(chat_id='383326777', 
                             text='A single message with 30s delay')


def main():
    print(datetime.now())
#     create_tables()
    updater = Updater(
        token = '1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8',
        use_context=True,
    )
    j = updater.job_queue
    j.run_once(callback_30, 30)
#     updater.dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=message_handler))
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
