import requests, re
from time import sleep
from bs4 import BeautifulSoup
import requests	
url = "https://api.telegram.org/bot1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8/"
url_t = "https://www.sports.ru/"
team1 = '1'
team2 = '2'
team3 = '3'
team4 = '4'
team5 = '5'
team6 = '6'

def get_updates_json(request, offset=None):  
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(request + 'getUpdates', data=params)
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
     if message == 'liverpool' or message == '/liverpool':
         print('1')
         send_mess(chat, team1)
     elif message == 'arsenal' or message == '/arsenal':
         print('2')
         send_mess(chat, team2)
     elif message == 'chelsea' or message == '/chelsea':
         print('3')
         send_mess(chat, team3)
     elif message == 'real' or message == '/real':
         print('4')
         send_mess(chat, team4)
     elif message == 'barcelona' or message == '/barcelona' or message == 'barsa':
         print('5')
         send_mess(chat, team5)
     elif message == 'mu' or message == '/mu' or message == 'mu':
         print('6')
         send_mess(chat, team6)
     else:
         send_mess( chat,'Используйте команды начинающиеся с /')


def next_match(team):
     print('+')
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
    print('kirvoman')
    team1 = next_match('liverpool')
    team2 = next_match('arsenal')
    team3 = next_match('chelsea')
    team4 = next_match('real')
    team5 = next_match('barcelona')
    team6 = next_match('mu')
    
    print('updated')
def main():
    print("i was here")
    update_id = last_update(get_updates_json(url))['update_id']
    update_data()
    print(team1)
    while True:
        json = last_update(get_updates_json(url,update_id))
        print(json)
        if json == None:
              continue
        delay = update_id - json['update_id']
        print(update_id)
        print(json['update_id'])
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
            print(len(results))
            prev = results[total_updates + delay]
            message, author = get_mess(prev)
            message = message.lower()
            chat = get_chat_id(prev)
            action(message, chat)
            update_id += 1
        else:
            update_data()
        sleep(1)       

if __name__ == '__main__':  
    main()
