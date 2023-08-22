#!/usr/bin/env python3
import datetime
from urllib.request import urlopen
from telebot.types import Message
from telebot import types
import telebot
import urllib3
import requests
import logging


bot = telebot.TeleBot(os.environ.get('TLGRM_TOKEN'))
logging.basicConfig(filename="Telebot.log", level=logging.INFO)
time = datetime.datetime.today()
elsevier_token = os.environ.get('ELSEVIER_TOKEN')
elsevier_apikey = os.environ.get('ELSEVIER_APIKEY')

@bot.message_handler(commands=['start'])
@bot.edited_message_handler(commands=['start'])
def command_start(message: Message):
    bot.send_message(message.chat.id, 'Доброго дня, ' + message.from_user.first_name)
    help_text = "Список команд:\n\n" + "/start - почати роботу з ботом " + "\n/help - список команд" + "\n/issn - пошук видання по issn-номеру" + "\n/doi - пошук статті за doi-номером"
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['help'])
@bot.edited_message_handler(commands=['help'])
def command_help(message: Message):
    help_text = "Список команд:\n\n" + "/start - почати роботу з ботом " + "\n/help - список команд" + "\n/issn - пошук видання по issn-номеру" + "\n/doi - пошук статті за doi-номером"
    help_text += "\n\n Довідка:"
    help_text += "\n\nСередній показник характеризує середню кількість цитат, отриманих кожним документом, опублікованим в періодичному виданні."
    help_text += "\n\nРейтинг SJR оцінює зважене кількість цитат, отриманих серією публікацій. Зважена оцінка цитування залежить від галузі знань і престижності (SJR) цитує періодичного видання."
    help_text += "\n\nНормований за джерелами рівень цитованості статті (SNIP) - характеризує кількість фактично отриманих цитат в ставленні до очікуваного кількості для галузі знань серії публікацій."
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['issn'])
@bot.edited_message_handler(commands=['issn'])
def command_handler(message: Message):
    isn = bot.send_message(chat_id=message.chat.id,
                           text='Пошук по Scopus\nВведіть ISSN номер формату "XXXXXXXX" або "XXXX-XXXX" ')
    bot.register_next_step_handler(isn, responses_issn)


def responses_issn(message: Message):
    global response_issn
    time = datetime.datetime.today()

    try:
        issn = message.text
        url = 'https://api.elsevier.com/content/serial/title/issn/' + issn + '?apiKey=' + elsevier_token
        logging.info("\n\n[" + str(time) + "] - ISSN request:" +
                     "\nUser: " + str(message.chat.username) + "\nISSN - " + str(issn) + "\nAPI url: " + str(
            url) + "\nScanning JSON...\n\n\n")

        # alternative pycurl
        # data = json.loads(urlopen(url).read().decode("utf-8"))

        # pycurl
        headers = {
            'Accept': 'application/json',
        }

        params = (
            ('apiKey', elsevier_apikey),
        )

        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        # type editions
        try:
            response_issn = "Тип видання: " + str(data["serial-metadata-response"]["entry"][0]["prism:aggregationType"])
        except Exception:
            logging.error("Error ISSN request - type editions! Not specified")

        # title
        try:
            response_issn += "\nНазва: " + str(data["serial-metadata-response"]["entry"][0]["dc:title"])
        except Exception:
            logging.error("Error ISSN request - title! Not specified")

        # publisher
        try:
            response_issn += "\nВидавець: " + str(data["serial-metadata-response"]["entry"][0]["dc:publisher"])
        except Exception:
            logging.error("Error ISSN request - publisher! Not specified")

        # issn
        try:
            response_issn += "\nISSN: " + str(data["serial-metadata-response"]["entry"][0]["prism:issn"])
        except Exception:
            logging.error("Error ISSN request - issn! Not specified")

        # e-issn
        try:
            response_issn += "\nonline-ISSN: " + str(data["serial-metadata-response"]["entry"][0]["prism:eIssn"])
        except Exception:
            logging.error("Error ISSN request - e-issn! Not specified")

        # subject-area
        try:
            response_issn += "\nГалузь знань: " + str(
                data["serial-metadata-response"]["entry"][0]["subject-area"][0]["$"])
        except Exception:
            logging.error("Error ISSN request - subject-area! Not specified")

        # indicators journal
        try:
            response_issn += "\nСередній показник цитування за " + str(
                data["serial-metadata-response"]["entry"][0]["citeScoreYearInfoList"][
                    "citeScoreCurrentMetricYear"]) + "р. - " + str(
                data["serial-metadata-response"]["entry"][0]["citeScoreYearInfoList"]["citeScoreCurrentMetric"])  # 2017
        except Exception:
            logging.error("Error ISSN request - citeScoreLastYear! Not specified")

        try:
            response_issn += "\nСередній показник цитування за " + str(
                data["serial-metadata-response"]["entry"][0]["citeScoreYearInfoList"][
                    "citeScoreTrackerYear"]) + "р. - " + str(
                data["serial-metadata-response"]["entry"][0]["citeScoreYearInfoList"]["citeScoreTracker"])  # 2018
        except Exception:
            logging.error("Error ISSN request - citeScoreThatYear! Not specified")

        # SJR
        try:
            response_issn += "\nSJR за " + str(
                data["serial-metadata-response"]["entry"][0]["SJRList"]["SJR"][0]["@year"]) + " р. - " + str(
                data["serial-metadata-response"]["entry"][0]["SJRList"]["SJR"][0]["$"])
        except Exception:
            logging.error("Error ISSN request - SJR! Not specified")

        # SNIP
        try:
            response_issn += "\nSNIP за " + str(
                data["serial-metadata-response"]["entry"][0]["SNIPList"]["SNIP"][0]["@year"]) + " р. - " + str(
                data["serial-metadata-response"]["entry"][0]["SNIPList"]["SNIP"][0]["$"])
        except Exception:
            logging.error("Error ISSN request - SNIP! Not specified")

        # link to journal page
        try:
            response_issn += "\nПосилання: " + str(data["serial-metadata-response"]["entry"][0]["link"][0]['@href'])
        except Exception:
            logging.error("Error ISSN request - link! Not specified")
        bot.send_message(message.chat.id, response_issn)

    except Exception:
        bot.send_message(message.chat.id, "Невірний ISSN номер, спробуйте знову та введіть /issn")
        logging.error("\n[Error] ISSN request - Decoding JSON has failed - Invalid ISSN" +
                      "\n\n[" + str(time) + "] - ISSN request:" + "User: " + str(message.chat.username) + "\nISSN - " + str(
                issn) + "\nAPI url: " + str(url) + "\n\n\n")


@bot.message_handler(commands=['doi'])
@bot.edited_message_handler(commands=['doi'])
def command_handler(message: Message):
    doi_c = bot.send_message(chat_id=message.chat.id,
                             text='Пошук статті по Scopus\nВведіть doi-номер за прикладом - 10.1186/s13661-019-1120-5')
    bot.register_next_step_handler(doi_c, responses_doi)


def responses_doi(message: Message):
    global response_doi
    time = datetime.datetime.today()

    try:
        doi = message.text
        url = 'https://api.elsevier.com/content/abstract/doi/' + doi + '?apiKey=' + elsevier_token
        logging.info("\n[" + str(time) + "] - Doi request:" +
                     "\nUser: " + str(message.chat.username) + "\ndoi - " + str(doi) + "\nAPI url: " + str(
            url) + "\nScanning JSON...\n\n\n")

        # pycurl
        headers = {
            'Accept': 'application/json',
        }

        params = (
            ('apiKey', elsevier_apikey),
        )

        r = requests.get(url, headers=headers, params=params)
        data_doi = r.json()

        # title journal
        try:
            response_doi = "Назва журналу: " + str(
                data_doi["abstracts-retrieval-response"]["coredata"]["prism:publicationName"])
        except Exception:
            logging.error("Error doi request - title journal! Not specified")

        # issn, e-issn
        try:
            response_doi += "\nISSN: " + str(data_doi["abstracts-retrieval-response"]["coredata"]["prism:issn"])
        except Exception:
            logging.error("Error doi request - issn! Not specified")

        # title article
        try:
            response_doi += "\nНазва статті: " + str(data_doi["abstracts-retrieval-response"]["coredata"]["dc:title"])
        except Exception:
            logging.error("Error doi request - title article! Not specified")

        # author firstname, surname
        try:
            response_doi += "\nАвтор: " + str(
                data_doi["abstracts-retrieval-response"]["coredata"]["dc:creator"]["author"][0]["preferred-name"][
                    "ce:surname"]) + " " + str(
                data_doi["abstracts-retrieval-response"]["coredata"]["dc:creator"]["author"][0]["preferred-name"][
                    "ce:given-name"])
        except Exception:
            logging.error("Error doi request - author name! Not specified")

        # country, city
        try:
            response_doi += "\nКраїна, місто: " + str(
                data_doi["abstracts-retrieval-response"]["affiliation"]["affiliation-country"]) + ", " + str(
                data_doi["abstracts-retrieval-response"]["affiliation"]["affiliation-city"])
        except Exception:
            logging.error("Error doi request - country, city! Not specified")

        # date cover
        try:
            response_doi += "\nДата публікації: " + str(
                data_doi["abstracts-retrieval-response"]["coredata"]["prism:coverDate"])
        except Exception:
            logging.error("Error doi request - data cover! Not specified")

        # publisher
        try:
            response_doi += "\nВидавець: " + str(data_doi["abstracts-retrieval-response"]["coredata"]["dc:publisher"])
        except Exception:
            logging.error("Error doi request - publisher! Not specified")

        # doi
        try:
            response_doi += "\ndoi-номер: " + str(data_doi["abstracts-retrieval-response"]["coredata"]["prism:doi"])
        except Exception:
            logging.error("Error doi request - doi! Not specified")

        # volume, issue, pages
        try:
            response_doi += "\nТом: " + str(data_doi["abstracts-retrieval-response"]["coredata"]["prism:volume"])

            response_doi += "\nВипуск: " + str(
                data_doi["abstracts-retrieval-response"]["coredata"]["prism:issueIdentifier"])

            response_doi += "\nСторінки: " + str(
                data_doi["abstracts-retrieval-response"]["coredata"]["prism:pageRange"])
        except Exception:
            logging.error("Error doi request - volume, issue, pages! Not specified")

        # count - citedby
        try:
            response_doi += "\nКількість цитувань: " + str(
                data_doi["abstracts-retrieval-response"]["coredata"]["citedby-count"])
        except Exception:
            logging.error("Error doi request - citedby! Not specified")

        # link to article
        try:
            response_doi += "\n\nПосилання: " + str(
                data_doi["abstracts-retrieval-response"]["coredata"]["link"][1]["@href"])
        except Exception:
            logging.error("Error doi request - link! Not specified")
        bot.send_message(message.chat.id, response_doi)

    except Exception:
        bot.send_message(message.chat.id, 'Невірний doi-номер, спробуйте знову та введіть /doi')
        logging.error("\n[Error] Doi request - Decoding JSON has failed - Invalid doi" + "\n[" + str(time) + "] - Doi request:" +
                     "\nUser: " + str(message.chat.username) + "\ndoi - " + str(doi) + "\nAPI url: " + str(
            url) + "\n\n\n")


@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types=['text'])
def echo_message(message: Message):
    bot.reply_to(message, 'Чтобы произвести какие-то действия введите команду\nСо списком команд можно '
                          'ознакомиться с помощью - /help')
    return


bot.polling()

# @bot.message_handler(commands=['doi'])
# @bot.edited_message_handler(commands=['doi'])
# def command_handler(message: Message):
#     btn_scopus = types.InlineKeyboardButton(text='Scopus', callback_data='scopus')
#     # btn_wos = types.InlineKeyboardButton(text='WoS', callback_data='wos')
#     markup = types.InlineKeyboardMarkup()
#     markup.add(btn_scopus)  # ,btn_wos
#     bot.send_message(message.chat.id, "Виберіть базу індексування для пошуку:", reply_markup=markup)
#     # bot.register_next_step_handler(message.chat.id, b_scopus, switch_scopus)
