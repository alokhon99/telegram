import requests, re
from time import sleep
from bs4 import BeautifulSoup
import requests
import pytz
import datetime

url = "https://api.telegram.org/bot1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8/"
url_t = "https://www.sports.ru/"
team1 = '1'
team2 = '2'
team3 = '3'
team4 = '4'
team5 = '5'
team6 = '6'
team7 = '7'
team8 = '8'

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
    print("I send it"+text+str(chat))
    return response

def innerHTML(element):
    """Returns the inner HTML of an element as a UTF-8 encoded bytestring"""
    return element.encode_contents()

def get_mess(update):
    message = update['message']['text']
    author = update['message']['chat']['first_name']
    return message, author;

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
         send_mess(chat, team1)
     elif message == 'arsenal' or message == '/arsenal':
         send_mess(chat, team2)
     elif message == 'chelsea' or message == '/chelsea':
         send_mess(chat, team3)
     elif message == 'real' or message == '/real':
         send_mess(chat, team4)
     elif message == 'barcelona' or message == '/barcelona' or message == 'barsa':
         send_mess(chat, team5)
     elif message == 'mu' or message == '/mu' or message == 'mu':
         send_mess(chat, team6)
     elif message == 'juventus' or message == '/juventus' or message == 'juve' or message == 'cr7' or message == 'penaldu':
         send_mess(chat, team7)
     elif message == 'manchester-city' or message == '/city' or message == 'city' or message == 'bir qop pul' or message == 'kalbosh' or message == 'kal':
         send_mess(chat, team8)       
     else:
         send_mess( chat,'Используйте команды начинающиеся с /')


def next_match(team):
     html_content = requests.get(url_t + team + '/').text
     soup = BeautifulSoup(html_content, "lxml")
     contents=soup.find_all('div', class_='commands')
     next_match = contents[1]
     team1 = next_match.find_all('span')[1].text
     team2 = next_match.find_all('span')[3].text
     details = soup.find_all('div', class_='score-descr')[1]
     dt_full = details.text
     dt_full = dt_full.replace(next_match.text,'')
     dt_words = dt_full.split(' ')
     date = dt_words[0].lstrip() + ' ' + dt_words[1]
     time = dt_words[2]
     tournament = ''
     for w in dt_words[3:]:
            tournament = tournament + w + ' '
     tournament = tournament.replace('|\n', '').lstrip()
     temp = time.split(':')
     hour = int(temp[0])
     hour = hour + 2
     if hour > 23:
         hour = hour - 24
     hour = str(hour)
     minute = temp[1]
     time = hour + ':' + minute
     new_m = 'Следующий матч: ' + '\n' + tournament + date+ ' ' + time + '\n' +  team1 + ' - ' +  team2
     return new_m

def update_data():
    global team1 
    global team2 
    global team3 
    global team4 
    global team5 
    global team6
    global team7 
    global team8
    team1 = next_match('liverpool')
    team2 = next_match('arsenal')
    team3 = next_match('chelsea')
    team4 = next_match('real')
    team5 = next_match('barcelona')
    team6 = next_match('mu')
    team7 = next_match('juventus')
    team8 = next_match('manchester-city')
    print('updated')
def main():
    update_id = last_update(get_updates_json(url))['update_id']
    update_data()
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
            message, author = get_mess(json)
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
            message, author = get_mess(prev)
            message = message.lower()
            chat = get_chat_id(prev)
            action(message, chat)
            update_id += 1
        if utc_timestamp.astimezone(pytz.timezone('Asia/Tashkent')) == datetime.time(0, 0):
            update_data()
        sleep(1)       

if __name__ == '__main__':  
    main()
