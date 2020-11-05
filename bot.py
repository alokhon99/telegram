import requests, re
from time import sleep
from bs4 import BeautifulSoup
import requests	
url = "https://api.telegram.org/bot1304159941:AAFZS7emVJ-dmkbGlOmjdZV6gnufSfdgBX8/"
url_t = "https://www.sports.ru/"

def get_updates_json(request):  
    params = {'timeout': 100, 'offset': None}
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
         next_match('liverpool', chat)
     elif message == 'arsenal' or message == '/arsenal':
         print('2')
         next_match('arsenal', chat)
     elif message == 'chelsea' or message == '/chelsea':
         print('3')
         next_match('chelsea', chat)
     elif message == 'real' or message == '/real':
         print('4')
         next_match('real', chat)
     elif message == 'barcelona' or message == '/barcelona' or message == 'barsa':
         print('5')
         next_match('barcelona', chat)
     else:
         send_mess( chat,'Используйте команды начинающиеся с /')


def next_match(team, chat):
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
     send_mess(  chat,new_m)


def main():  
    update_id = last_update(get_updates_json(url))['update_id']
    while True:
        json = last_update(get_updates_json(url))
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
            prev = results[total_updates - delay]
            message, author = get_mess(prev)
            message = message.lower()
            chat = get_chat_id(prev)
            action(message, chat)
            update_id += 1
        sleep(1)       

if __name__ == '__main__':  
    main()
