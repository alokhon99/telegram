import requests, re
import telegram.ext
import time
from time import sleep
from bs4 import BeautifulSoup
import requests
import pytz
from datetime import datetime, timedelta
import os
import emoji
import psycopg2
from telegram import Update, ParseMode
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from classes import Match
from classes import User 
from classes import Team
from classes import RU_MONTH_VALUES
from classes import int_value_from_ru_month
DATABASE_URL = os.environ['DATABASE_URL']

url = "https://api.telegram.org/bot1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8/"
url_t = "https://www.sports.ru/"

team1 = Team('liverpool')
team2 = Team('arsenal')
team3 = Team('chelsea')
team4 = Team('real')
team5 = Team('barcelona')
team6 = Team('mu')
team7 = Team('juventus')
team8 = Team('manchester-city')
team9 = Team('milan')
team10 = Team('tottenham')
teams = {'Liverpool': team1, 'Arsenal': team2, 'Chelsea': team3, 'Real Madrid': team4, 'Barcelona': team5, 'Manchester United': team6, 'Juventus': team7, 'Manchester City': team8, 'Milan': team9, 'Tottenham': team10}
users = []

updater = Updater(
        token = '1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8',
        use_context=True,
    )


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
    return users

def get_keyboard(n, fav=None):
        if n == 0:
            return ReplyKeyboardMarkup(
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
                        KeyboardButton(text= fav+" \u2764\ufe0f")
                                ],
                        [KeyboardButton(text="Bugun")],
                        [KeyboardButton(text="Taklifim bor!")],
                ],
                resize_keyboard=True,)
        elif n == 1:
            return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Angliya')],[KeyboardButton(text='Ispaniya')],[KeyboardButton(text='Italiya')],[KeyboardButton(text="Bugun")],],resize_keyboard=True,)    
        elif n == 2:
            return ReplyKeyboardMarkup(
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
                    KeyboardButton(text='Tottenham')
                    ],
                [KeyboardButton(text='Orqaga')],
            ],
            resize_keyboard=True,)
        elif n == 3:
            return ReplyKeyboardMarkup(
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
        elif n == 4:
            return ReplyKeyboardMarkup(
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
        elif n == 5:
            return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Orqaga')],
            ],
            resize_keyboard=True,)
        elif n == 6:
            return ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borishni bekor qilish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        elif n == 7:
            return ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        else:
            return ReplyKeyboardMarkup(
            keyboard=[
                    [KeyboardButton(text='Yuborish')],
                [KeyboardButton(text='Orqaga')],
            ],
            resize_keyboard=True,)



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
    chat_id = int(chat_id)
    sql = """ UPDATE users
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
#         cur.execute(sql,(fav, chat_id))
        cur.execute(sql,(fav, chat_id,))
        print('executed')
        print('row count '+str(cur.rowcount))
        # get the generated id back
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
def change_to_no():
    print('insert')
    global DATABASE_URL
    sql = """ UPDATE users
             SET fav = 'No'
             WHERE fav = NULL;"""
    print('update')
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print('connect set')
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
#         cur.execute(sql,(fav, chat_id))
        cur.execute(sql)
        print('executed')
        print('row count '+str(cur.rowcount))
        # get the generated id back
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insert_name(chat_id, name):
    print('insert name')
    global DATABASE_URL
    chat_id = int(chat_id)
    sql = """ UPDATE users
             SET username = %s
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
#         cur.execute(sql,(fav, chat_id))
        cur.execute(sql,(name, chat_id,))
        print('executed')
        print('row count '+str(cur.rowcount))
        # get the generated id back
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

def get_user(chat_id):
    print('select')
    global DATABASE_URL
    sql = """SELECT * FROM users
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



def button_country_handler(update: Update, context: CallbackContext, message):
    print("handlerga keldi")
    print("bu "+message+" message")
    if message == 'Angliya':
        reply_markup = get_keyboard(2)
    elif message == 'Ispaniya':
        reply_markup = get_keyboard(3)
    elif message == 'Italiya':
        reply_markup = get_keyboard(4)
        
    update.message.reply_text(
        text=message+' jamoasini tanlang',
        reply_markup=reply_markup,
    )
      
def message_handler(update: Update, context: CallbackContext):
    message = update.message.text.replace(" \u2764\ufe0f",'')
    print(update.message.chat_id)
    name = update.message.from_user.first_name
    if update.message.from_user.last_name != None:
        name = name + update.message.from_user.last_name
    print(name)
    type(update.message.chat_id)
    global users
    x = None
    for u in users:
        if u.chat_id == update.message.chat_id:
            x = u
            break
    if x == None:
        x = User(update.message.chat_id)
        u = get_user(update.message.chat_id)
        if u == None:
            print("if")
            insert_user(update.message.chat_id)
            insert_fav(update.message.chat_id, 'No')
        u = get_user(update.message.chat_id)
        print(u)
        print(name)
        if u[1] != name:
                insert_name(update.message.chat_id, name)
        if u[2] == None or u[2] == '':
                insert_fav(update.message.chat_id, 'No')
        else:
                print('elsega kirdi')
                print(u[2])
                x.fav = u[2]
        users.append(x)
    else:
        u = get_user(update.message.chat_id)
        if u[1] != name:
                insert_name(update.message.chat_id, name)
    users_db()
    print(x.fav)
    if x.fav != 'No':
        reply_markup = get_keyboard(0,x.fav)
    else:
        reply_markup = get_keyboard(1)
    if message == "Orqaga":
        message = x.get_back()
    if message == 'test':
        today = """<pre>
| Tables   |      Are      |  Cool |
|----------|:-------------:|------:|
| col 1 is |  left-aligned | $1600 |
| col 2 is |    centered   |   $12 |
| col 3 is | right-aligned |    $1 |
</pre>"""
        update.message.reply_text(parse_mode=ParseMode.HTML,
        text=today,
        reply_markup=get_keyboard(5),
        )
        return     
        
    if message == 'Bugun':
        today = 'Сегодняшние матчи:\n\n'
        flag = 0
        for key in teams:
                team = teams[key]
                match = team.next
                if match.is_today():
                        flag = 1
                        today = today + match.get_message() + '\n' + '\n'
        if flag == 0:
                e = "\N{pensive face}"
                today = 'Увы, сегодняшние матчи не найдено' + e
        
        update.message.reply_text(
        text=today,
        reply_markup=get_keyboard(5),
        )
        return 
    if message == 'Angliya' or message == 'Ispaniya' or message == 'Italiya':
        print("keldi buyoga")
        x.league = message
        x.state = 1
        return button_country_handler(update=update, context=context, message=message)
    elif message == 'Tottenham' or message == 'Liverpool' or message == 'Arsenal' or message == 'Chelsea' or message == 'Real Madrid' or message == 'Barcelona' or message == 'Manchester United' or message == 'Juventus' or message == 'Manchester City' or message == 'Milan':
        if x.fav == message:
                print('kirdi')
                reply_markup = get_keyboard(6)
        else:
                print('buyaqqqa')
                reply_markup = get_keyboard(7)
        x.team = message
        x.state = 2
        update.message.reply_text(
        text="Izlayotgan ma'lumotingizni tanlang",
        reply_markup=reply_markup,
        )
        return 
    elif message == "Keyingi o'yin" or message =="So'nggi o'yin":
        m = message
        print('keyingi oyin')
        message = x.team
        if message == x.fav:
                reply_markup = get_keyboard(6)
        else:
                reply_markup = get_keyboard(7)
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
        elif message == 'Tottenham' or message == '/tottenham' or message == 'tot':
            update.message.reply_text(
             text= team10.get(m),
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
    elif message == 'Kuzatib borishni bekor qilish':
        x.fav = 'No'
        insert_fav(x.chat_id,'No')
        text = 'Endi siz '+x.team+'ni kuzatib bormaysiz'
        print('+')
        update.message.reply_text(
           text= text,
           reply_markup=get_keyboard(7),
        )
    elif message == "Kuzatib borish":
        insert_fav(str(x.chat_id), x.team)
        global updater
        f = x.fav
        x.fav = x.team
        update.message.reply_text(
                text= x.team + " jamoasi Sevimlilar bo'limiga tushdi",
                reply_markup=get_keyboard(6),)
        if f != 'No':
              obuna(updater.job_queue, x, f)
              return
        obuna(updater.job_queue, x)
        return
    elif message == "Taklifim bor!":
        x.state = 9
        update.message.reply_text(
                text= "Taklifingizni qisqacha yozib, bizga yuboring",
                reply_markup=get_keyboard(5),)
        return
    elif message == 'tabletest':
        context.bot.send_photo(x.chat_id, 'https://hcti.io/v1/image/f0b72c6e-16dc-4487-9a11-5134d069f053')
        return
    else:
        if x.state == 9 and message != 'any':
                update.message.reply_text(
                text= "Taklifingiz qabul qilindi. E'tiboringiz uchun rahmat!",
                reply_markup=get_keyboard(5),)
                context.bot.send_message(383326777, message + '\n' +name)
                x.state == 0
                return
        print(message)
        x.clear_history()
        text = 'Davlatni tanglang'
        if x.fav != 'No':
                reply_markup = get_keyboard(0,x.fav)
        else:
                reply_markup = get_keyboard(1)
        print('+')
        update.message.reply_text(
           text= text,
            reply_markup=reply_markup,
        )
def callback_update(context: telegram.ext.CallbackContext):
        global teams
        chat_id = context.job.context[0]
        job = context.job.context[1]
        for user in users:
                if user.chat_id == chat_id:
                        u = user
                        break
        for key in teams:
                if key == u.fav:
                        team = teams[key]
                        break
        team.next.update_as_next(team.name)
        team.prev.update_as_prev(team.name)
        if team.next.is_passed() == False:
                obuna(job, u)
        else:
               two_hour = timedelta(hours=2)
               job.run_once(callback=callback_update, when=two_hour,context= (chat_id, job)) 
def callback(context: telegram.ext.CallbackContext):
    print(context.job.context)
    chat_id = context.job.context[0]
    text = context.job.context[1]
    job = context.job.context[2]
    context.bot.send_message(chat_id=chat_id, 
                             text=text)
    two_hour = timedelta(hours=4)
    job.run_once(callback=callback_update, when=two_hour,context= (chat_id, job))

def obuna(job, x=None, old=' '):
    if x:
        team = teams.get(x.fav)
        print(str(x.chat_id)+old)
        print(job.get_jobs_by_name(str(x.chat_id)+old))
        for j in job.get_jobs_by_name(str(x.chat_id)+old):
                j.schedule_removal()
                print(str(x.chat_id)+old)
        print('bu kevoti '+x.fav)
        match = team.next
        print('obuna test1')
        dt = match.date.split(' ')
        print('obuna test1')
        day = int(dt[0])
        print('obuna test1')
        mon = int(int_value_from_ru_month(dt[1]))
        print('obuna test1')
        ten_minute = timedelta(minutes=10)
        print('obuna test2')
        hour = int(match.hour)
        print('obuna test3')
        minute = int(match.minute)
        print('obuna test4')
        d = datetime(2021, mon, day, hour, minute)
        if hour < 12:
                d = d + timedelta(days=1)
        print('obuna test5')
        tshv = pytz.timezone("Asia/Tashkent")
        print('obuna test6')
        d = tshv.localize(d)
        print('obuna test7')
        print(d-ten_minute)
        a = job.run_once(callback=callback, when=d-ten_minute,context= (x.chat_id, match.get_notification(), job), name = str(x.chat_id)+x.fav)
        print(str(x.chat_id)+x.fav + ' job qoshildi queuega')
    else:
        print('obuna')
        users = users_db()
        print(users)
        for user in users:
            print(user)
            if user[2] != 'No' and user[2] != None and user[2] != ' ':
                team = teams.get(user[2])
                match = team.next
                dt = match.date.split(' ')
                day = int(dt[0])
                mon = int(int_value_from_ru_month(dt[1]))
                ten_minute = timedelta(minutes=10)
                hour = int(match.hour)
                minute = int(match.minute)
                d = datetime(2021, mon, day, hour, minute)
                tshv = pytz.timezone("Asia/Tashkent")
                d = tshv.localize(d)
                print(d)
                if hour < 12:
                        d = d + timedelta(days=1)
                d = d - ten_minute
                print(d)
                a = job.run_once(callback=callback, when=d,context= (int(user[0]), match.get_notification(), job), name = str(user[0])+user[2])      

def main():
    
    os.environ['TZ'] = 'Asia/Tashkent'
    time.tzset()
    datetime_object = datetime.strptime('11/17/2020 16:16:00.000000', '%m/%d/%Y %H:%M:%S.%f')
    print(datetime_object-datetime.now())
    create_tables()
    global updater
    j = updater.job_queue
    tshv = pytz.timezone("Asia/Tashkent")
    datetime_object = tshv.localize(datetime_object)
#     change_to_no()
    obuna(j)
    
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
