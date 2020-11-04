import requests, re
from time import sleep
from bs4 import BeautifulSoup
import requests	
url = "https://api.telegram.org/bot1267299041:AAGA-G9FCLj1EMTJ4DTkvWp2SWskNnsgq6s/"
liverpool ="http://liverpool-fan.ru/"

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
    
def main():  
    update_id = last_update(get_updates_json(url))['update_id']
    while True:
        if update_id == last_update(get_updates_json(url))['update_id']:
            message, author = get_mess(last_update(get_updates_json(url)))
            print( last_update(get_updates_json(url)))
#            send_mess('383326777', message+'\n'+author)
            message = message.lower()
            message = re.sub(r'men\b','man', message)
            message = re.sub(r'sen\b','san', message)
            message = re.sub(r'iq\b','u', message)
            message = re.sub(r'men\b','man', message)
            message = re.sub(r'mayman\b','miman', message)
            message = re.sub(r'maysan\b','misan', message)
            message = re.sub(r'yab','vo', message)
            if message == 'liverpool':
                html_content = requests.get(liverpool).text
                soup = BeautifulSoup(html_content, "lxml")
                contents=soup.find_all('table')
                table = contents[3]
                table = table.find('table')
                box = table.find('div', class_="boxContent")
                team = box.find('b')
                center = box.find('div')
                text = center.text
                words = text.split('\n')
                new_m = ' '
                day = words[4]
                time = words[5]
                temp = time.split(' ')
                time = temp[1]
                temp = time.split(':')
                hour = int(temp[0])
                hour = hour + 2
                if hour > 23:
                    hour = hour - 24
                str(hour)
                minute = temp[1]
                new_m = team.text + '\n' + day + '\n' + hour + ':' + minute
                send_mess(  get_chat_id(last_update(get_updates_json(url))),new_m)
            else:
                send_mess(  get_chat_id(last_update(get_updates_json(url))),message)
#            send_mess(get_chat_id(last_update(get_updates_json(url))), 'test')
            update_id += 1
        sleep(1)       

if __name__ == '__main__':  
    main()
