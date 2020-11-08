import requests, re
from time import sleep
from bs4 import BeautifulSoup
import requests
import pytz
import datetime

url = "https://api.telegram.org/bot1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8/"
url_t = "https://www.sports.ru/"


class Team:
    def __init__(self, name):
        print('init')
        self.name = name
        self.upd(name)
        
    def upd(self, name):
        print('upd')
        global url_t;
        
        html_content = requests.get(url_t + name + '/').text
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
        return 'Следующий матч: ' + '\n' + self.tournament + self.date+ ' ' + self.hour+':'+self.minute + '\n' +  self.team1 + ' - ' + self.team2
        
    name = 'team'
    team1 = 'team'
    team2 = 'opponent'
    hour = '00'
    minute = '00'
    date = '12'
    tounament = 'epl'
    
   

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
         send_mess(chat, team1.get_message())
     elif message == 'arsenal' or message == '/arsenal':
         send_mess(chat, team2.get_message())
     elif message == 'chelsea' or message == '/chelsea':
         send_mess(chat, team3.get_message())
     elif message == 'real' or message == '/real':
         send_mess(chat, team4.get_message())
     elif message == 'barcelona' or message == '/barcelona' or message == 'barsa':
         send_mess(chat, team5.get_message())
     elif message == 'mu' or message == '/mu' or message == 'mu':
         send_mess(chat, team6.get_message())
     elif message == 'juventus' or message == '/juventus' or message == 'juve' or message == 'cr7' or message == 'penaldu':
         send_mess(chat, team7.get_message())
     elif message == 'manchester-city' or message == '/city' or message == 'city' or message == 'bir qop pul' or message == 'kalbosh' or message == 'kal':
         send_mess(chat, team8.get_message())
     elif message == '1492312':
         send_mess(chat, "yusuf алкаш buni hamma biladi")
     else:
         send_mess( chat,'Используйте команды начинающиеся с /')


def main():
    update_id = last_update(get_updates_json(url))['update_id']
    global team1 = Team('liverpool')
    global team2 = Team('arsenal')
    global team3 = Team('chelsea')
    global team4 = Team('real')
    global team5 = Team('barcelona')
    global team6 = Team('mu')
    global team7 = Team('juventus')
    global team8 = Team('manchester-city')
    while True:
        print("loop")
        json = last_update(get_updates_json(url,update_id))
        if json == None:
              continue
        delay = update_id - json['update_id']
        print(delay)
        if delay == 0:
#             message = re.sub(r'men\b','man', message)
#             message = re.sub(r'sen\b','san', message)
#             message = re.sub(r'iq\b','u', message)
#             message = re.sub(r'men\b','man', message)
#             message = re.sub(r'mayman\b','miman', message)
#             message = re.sub(r'maysan\b','misan', message)
#             message = re.sub(r'yab','vo', message)
            message = get_mess(json)
            message = message.lower()
            chat = get_chat_id(json)
            action(message, chat)
            update_id += 1
        elif delay < 0:
            bigJ = get_updates_json(url)
            results = bigJ['result']
            if len(results) == 0:
                return
            total_updates = len(results) - 1
            prev = results[total_updates + delay]
            message = get_mess(prev)
            message = message.lower()
            chat = get_chat_id(prev)
            action(message, chat)
            update_id += 1
        sleep(1)       

if __name__ == '__main__':  
    main()
