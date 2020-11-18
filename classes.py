import requests, re
import telegram.ext
import time
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

def int_value_from_ru_month(date_str):
    print('convert1')
    print(date_str)
    for k, v in RU_MONTH_VALUES.items():
        print('convert1')
        date_str = date_str.replace(k, str(v))
    print(date_str)
    return date_str

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
        print('is_passed1')
        dt = self.date.split(' ')
        day = str(int(dt[0]))
        print('is_passed2')
        print(dt[1])
        mon = str(int_value_from_ru_month(dt[1]))
        print('is_passed3')
        print(day)
        print(type(day))
        print(mon)
        print(type(mon))
        date = datetime.strptime(day+'/'+mon+'/2020', "%d/%m/%Y").date()
        print('is_passed4')
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
