import requests, re
import telegram.ext
import time
from time import sleep
from bs4 import BeautifulSoup
import requests
import pytz
from datetime import datetime, timedelta
import os
import psycopg2
from telegram import Update
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
teams = {'Liverpool': team1, 'Arsenal': team2, 'Chelsea': team3, 'Real Madrid': team4, 'Barcelona': team5, 'Manchester United': team6, 'Juventus': team7, 'Manchester City': team8, 'Milan': team9}
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

def insert_name(chat_id, name):
    print('insert')
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
    
    
def message_handler(update: Update, context: CallbackContext):
    message = update.message.text
    print(update.message.chat_id)
    name = update.message.from_user.first_name
    if update.message.from_user.last_name != None:
        name = name + update.message.from_user.last_name
    type(update.message.chat_id)
    global users
    x = None
    for u in users:
        if u.chat_id == update.message.chat_id:
            x = u
            break
    if x == None:
        u = get_user(update.message.chat_id)
        if u == None:
            print("if")
            insert_user(update.message.chat_id)
            fav = None
        else:
            fav = u[2]
            if u[1] != name:
                insert_name(update.message.chat_id, name)
        x = User(update.message.chat_id)
        x.fav = fav
        users.append(x)
    users_db()
    if x.fav:
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
                        KeyboardButton(text=x.fav)
                                ],
                ],
                resize_keyboard=True,)
    else:
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
                text= "Profilaktika ishlari bo'lmoqda. E'tiboringiz uchun rahmat!" ,
                reply_markup=reply_markup,)
    return





    if message == 'Sevimli Jamoa':
        update.message.reply_text(
                text= x.fav,
                reply_markup=reply_markup,)
        return
    elif message == "Kuzatib borish":
        insert_fav(str(x.chat_id), x.team)
        global updater
        f = x.fav
        print(f)
        x.fav = x.team
        reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        update.message.reply_text(
                text= x.team + " jamoasi Sevimlilar bo'limiga tushdi",
                reply_markup=reply_markup,)
        if f != None:
              obuna(updater.job_queue, x, f)
              return
        obuna(updater.job_queue, x)
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
        print(x.fan)
        if message == x.fan:
                print('kirdi')
                reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borishni bekor qilish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        else:
                print('buyaqqqa')
                reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        update.message.reply_text(
        text="Izlayotgan ma'lumotingizni tanlang",
        reply_markup=reply_markup,
        )
        return 
    elif message == "Keyingi o'yin" or message =="So'nggi o'yin":
        m = message
        message = x.team
        if message == x.fan:
                reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borishni bekor qilish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        else:
                reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        if message == 'Liverpool' or message == '/liverpool':
            print('keldiiiiiik')
            print(m)
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
    elif message == 'Kuzatib borishni bekor qilish':
        if message == x.fan:
                reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borishni bekor qilish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        else:
                reply_markup = ReplyKeyboardMarkup( keyboard=[ [ KeyboardButton(text="Keyingi o'yin")],[KeyboardButton(text="So'nggi o'yin")],[KeyboardButton(text='Kuzatib borish')],[KeyboardButton(text='Orqaga')], ],resize_keyboard=True,)
        x.fan = None
        insert_fav(x.chat_id,'')
        text = 'Endi siz '+x.team+'ni kuzatib bormaysiz'
        print('+')
        update.message.reply_text(
           text= text,
            reply_markup=reply_markup,
        )
    else:
        x.clear_history()
        text = 'Davlatni tanglang'
        if x.fav:
                reply_markup = ReplyKeyboardMarkup(
                      keyboard=[
                               [
                                KeyboardButton(text='Angliya')],[
                                KeyboardButton(text='Ispaniya')],[
                                KeyboardButton(text='Italiya')],[
                                KeyboardButton(text=x.fav)],],
                                resize_keyboard=True,)
        else:
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
        team.next.update_as_next(u.fav)
        team.prev.update_as_prev(u.fav)
        if team.next.is_passed() == False:
                obuna(job, u)
        else:
               two_hour = timedelta(hours=2)
               job.run_once(callback=callback_update, when=two_hour,context= (x.chat_id, job)) 
def callback(context: telegram.ext.CallbackContext):
    chat_id = context.job.context[0]
    text = context.job.context[1]
    job = context.job.context[2]
    context.bot.send_message(chat_id=chat_id, 
                             text=text)
    two_hour = timedelta(hours=4)
    job.run_once(callback=callback_update, when=two_hour,context= (x.chat_id, job))

def obuna(job, x=None, old=' '):
    print('job')
    print(job)
    print('x')
    
    
    print(x)
    print('old')
    print(old)
    if x:
        team = teams.get(x.fav)
        print(str(x.chat_id)+old)
        print(job.get_jobs_by_name(str(x.chat_id)+old))
        for j in job.get_jobs_by_name(str(x.chat_id)+old):
                j.schedule_removal()
                print(str(x.chat_id)+old)
        print('bu kevoti '+x.fav)
        match = team.next
        dt = match.date.split(' ')
        day = int(dt[0])
        mon = int(int_value_from_ru_month(dt[1]))
        ten_minute = timedelta(minutes=10)
        hour = int(match.hour)
        minute = int(match.minute)
        d = datetime(2020, mon, day, hour, minute)
        print(d-ten_minute)
        tshv = pytz.timezone("Asia/Tashkent")
        d = tshv.localize(d)
        a = job.run_once(callback=callback, when=d,context= (x.chat_id, match.get_notification(), job), name = str(x.chat_id)+user[2])
    else:
        print('obuna')
        users = users_db()
        print(users)
        for user in users:
            print(user[2])
            if user[2]:
                team = teams.get(user[2])
                match = team.next
                dt = match.date.split(' ')
                day = int(dt[0])
                mon = int(int_value_from_ru_month(dt[1]))
                ten_minute = timedelta(minutes=10)
                hour = int(match.hour)
                minute = int(match.minute)
                d = datetime(2020, mon, day, hour, minute)
                print(d-ten_minute)
                tshv = pytz.timezone("Asia/Tashkent")
                d = tshv.localize(d)
                a = job.run_once(callback=callback, when=d,context= (int(user[0]), match.get_notification()), name = str(user[0])+user[2])      

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
