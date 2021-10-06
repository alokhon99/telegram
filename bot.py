from telegram.ext import Updater, CommandHandler, MessageHandler,    Filters, InlineQueryHandler
from bs4 import BeautifulSoup
import requests
gazprom  = 0
uzauto = 0
def sayhi(bot, job):
    global gazprom, uzauto
    page = requests.get("https://sapvalue.rbc.ru/nominees/7")
    soup = BeautifulSoup(page.content, 'html.parser')
    a = soup.find_all("div", class_="nominations__item-top")
    for A in a:
        H = A.find_all_next("h3", class_="nominations__item-tlt")
        for h in H:
            if h.text == "Узавтосаноат												":
                header = h.find_parent()
                ours = int(header.find_all_next("span", class_="like-heart__count")[0].text)
            elif h.text == "Газпром нефть												":
                header = h.find_parent()
                theirs = int(header.find_all_next("span", class_="like-heart__count")[0].text)
    
    if theirs > gazprom and gazprom != 0:
        job.context.message.reply_text("Gazprom + 1 vote. \n Uzauto - "+str(ours)+" Gazprom - "+str(theirs)+" \n Difference: "+str(ours-theirs)+"\n")
    gazprom = theirs
    uzauto = ours
    print(uzauto)
    print(gazprom)

def time(bot, update,job_queue):
    job = job_queue.run_repeating(sayhi, 5, context=update)

def main():
    updater = Updater("2077199343:AAF8ZLdUwGmeOlW7ligqAFKRW6sAKZnXXDc")
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text , time,pass_job_queue=True))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
