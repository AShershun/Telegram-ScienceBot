#coding:utf-

import telebot, config 

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привіт, я Telegram бот")

if __name__ == "__main__":
    bot.polling()
