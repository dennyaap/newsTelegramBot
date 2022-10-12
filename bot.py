import telebot
from telebot import types

from db import BotDB

import os
from dotenv import load_dotenv, find_dotenv

import requests

#database connection
BotDB = BotDB('users.db')

#using a global variable
load_dotenv(find_dotenv())
bot_token = os.getenv('BOT_TOKEN')
api_key = os.getenv('API_KEY')

#connect the telebot
telebot = telebot.TeleBot(bot_token)

commands = '/start - начать\n/about - о боте\n/categories - подписаться на категории\n/subscribes - мои подписки\n/unsubscribe - отписаться от категории\n/help - помощь'
about = 'привет меня зовут сладкий бот🙃 и я тебе покажу самые классные новости во всем Мире 🌍!'

@telebot.message_handler(commands=['start'])
def start(message):
    answer = ''
    user_id = message.chat.id

    if(not BotDB.find_user(user_id)):
        BotDB.add_user(user_id)
        answer = 'поздравляю с успешной регистрацией!🙃🤗\nВсе команды /help'
    else:
        answer = 'вы уже зарегистировались!🤗\nВсе команды /help'

    telebot.send_message(user_id, f'{message.from_user.first_name}, {answer}')

@telebot.message_handler(commands=['help'])
def send_help(message):
    telebot.send_message(message.chat.id, f'{message.from_user.first_name}, список доступных команд 🙃:\n{commands}')

@telebot.message_handler(commands=['about'])
def send_about(message):
    telebot.send_message(message.chat.id, f'{message.from_user.first_name}, ' + about + f'\n\nСписок доступных команд 🙃:\n{commands}')

@telebot.message_handler(commands=['categories'])
def send_categories(message):
    news_categories = BotDB.get_news_categories()
    markup = types.InlineKeyboardMarkup()
    
    for category in news_categories:
        markup.add(types.InlineKeyboardButton(category[1], callback_data=f'sub_category-{category[0]}'))

    telebot.send_message(message.chat.id, 'Список доступных категорий 🙃:', reply_markup=markup)

@telebot.callback_query_handler(func=lambda call: True)
def check_command(call):
    command = call.data.split('-')[0]
    data = call.data.split('-')[1]
    user_id = call.message.chat.id;
    result = ''

    if(command == 'sub_category'):
        category_id = data

        result = subscribe_category(user_id, category_id)
    elif(command == 'show_news'):
        category_news = data

        show_news_category(category_news, user_id)

        result = f'Новости за последнее время по категории: {category_news}\nПодписывайтесь на ещё больше новостных категорий!😉\n/categories'
    elif(command == 'unsub_category'):
        category_id = data

        print(BotDB.unsubscribe_category(user_id, category_id))

        result = f'Вы успешно отписались😉\n/subscribes - мои подписки'

    telebot.send_message(user_id, result)
    telebot.answer_callback_query(call.id)

@telebot.message_handler(commands=['unsubscribe'])
def unsubscribe_category(message):
    user_subscribes = BotDB.get_subscribes(message.chat.id)

    markup = types.InlineKeyboardMarkup()
    
    for category in user_subscribes:
        markup.add(types.InlineKeyboardButton(category[1], callback_data=f'unsub_category-{category[0]}'))

    telebot.send_message(message.chat.id, 'Выбери категорию от которой хотите отписаться 🙃:', reply_markup=markup)

@telebot.message_handler(commands=['subscribes'])
def get_user_subscribes(message):
    user_id = message.chat.id
    result = ''
    user_subscribes = BotDB.get_subscribes(user_id)
    markup = types.InlineKeyboardMarkup()
    
    if(bool(len(user_subscribes))):
        result = 'нажмите на интересующую вас категорию новостей:\n/unsubscribe - отписаться'
        for subscribe in user_subscribes:
            markup.add(types.InlineKeyboardButton(subscribe[1], callback_data=f'show_news-{subscribe[1]}'))
    else:
        result = 'вы не подписались ни на одну из категорий!\n/categories - сделайте это сейчас!😉'
    
    telebot.send_message(user_id, f'{message.from_user.first_name}, ' + result, reply_markup=markup)

def subscribe_category(user_id, category_id):
    category = BotDB.get_category(category_id)
    result = ''

    if(not BotDB.check_subscribe_category(user_id, category_id)):
        BotDB.subscribe_category(user_id, category_id)

        result = f'Вы успешно подписались на категорию {category[1]} 😉\n/subscribes - мои подписки'
    else:
        result = f'Вы уже подписаны на категорию {category[1]} 😉\n/subscribes - мои подписки'
       
    return result;
    
def send_image(chat_id, imgURL, caption):
    send_text = f'https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={chat_id}&parse_mode=HTML&caption={caption}&photo={imgURL}'
    response = requests.get(send_text)

    return response.json()

def show_news_category(category_news, chat_id):
    response = requests.get(f'https://newsapi.org/v2/top-headlines?category={category_news}&country=ru&apiKey={api_key}&pageSize=5')

    for post in response.json()['articles']:
        send_image(chat_id, post['urlToImage'], post['title'])



telebot.infinity_polling()