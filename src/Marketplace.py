# -*- coding: utf-8 -*-

import json
import logging
import Keyboards
import Sell
import Buy
import Navigation
import Feedback
from Settings import *

from sys import exit
from os import getenv
from re import search
from time import time
from time import sleep
from random import choice
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from Database import session, User, Item
from os.path import isfile as file_exists

# SQLAlchemy
from sqlalchemy import desc, asc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Boolean, text

# Telegram Bot
from telegram import ChatAction
from telegram.ext import Filters
from telegram.ext import Updater
from telegram import InputMediaPhoto
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler

# CHAT ACTION
def typing_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)
    return command_func

def photo_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_PHOTO)
        return func(update, context,  *args, **kwargs)
    return command_func

# START
def start(update, context):
    if session.query(User).filter_by(chat_id=update.message.chat_id).first():
        # User already exists
        context.bot.send_message(
            chat_id=update.message.chat_id, 
            text=statements['welcome_back'].replace("$$",update.message.chat.first_name), 
            reply_markup=Keyboards.Start,
            parse_mode="Markdown")
    else:
        # User not exists yet
        session.add(User(
            chat_id = update.message.chat_id,
            username = update.message.chat.username,
            first_name = update.message.chat.first_name))
        session.commit()
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['welcome'].replace("$$",update.message.chat.first_name),
            reply_markup=Keyboards.Start,
            parse_mode="Markdown")


# INSTRUCTIONS
def instructions(update, context):
    if context.user_data['section'] == "sell":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_instructions'],
            parse_mode="Markdown")
    elif context.user_data['section'] == "buy":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_instructions'],
            parse_mode="Markdown")

# INFORMATION
def information(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['information'],
        parse_mode="Markdown")

# BACK
def back(update, context):
    if context.user_data['section'] == "sell" \
        or context.user_data['section'] == "buy":
        context.user_data['last_items'] = None
        context.user_data['items_count'] = 0
        context.user_data['last_count'] = 0
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['main_menu'],
            reply_markup=Keyboards.Start,
            parse_mode="Markdown")

            
if __name__ == "__main__":

    # UPDATER, DISPATCHER, LOGGING AND LANGUAGE
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
        statements = json.load(lang_f)

    # HANDLERS
    start_handler = CommandHandler('start', start)
   
    feedback_handler = ConversationHandler(
        entry_points = [CommandHandler('feedback', Feedback.feedback)],
        states = {
            "DONE": [MessageHandler(Filters.text, Feedback.feedback_done)],
            "ANSWER": [MessageHandler(Filters.text, Feedback.feedback_answer)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"), Feedback.feedback_undo)]
    )
    #feedback_answer_handler = CommandHandler

    sell_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['sell']}$"), Sell.sell)
    buy_handler   = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['buy']}$"), Buy.buy)
    info_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['info']}$"), information)
    back_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['back']['back']}$"), back)
    instruction_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['instructions']}$"), instructions)

    sell_new_item_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['new_item']}$"), Sell.sell_new_item)],
        states = {
            "TITLE":  [MessageHandler(Filters.text, Sell.sell_title)],
            "PRICE":  [MessageHandler(Filters.text, Sell.sell_price)],
            "PHOTO":  [MessageHandler(Filters.photo, Sell.sell_photo),
                       MessageHandler(Filters.regex(rf"^{statements['keyboards']['skip']['skip']}$"), Sell.sell_photo)],
            "CYCLE":  [MessageHandler(Filters.text, Sell.sell_cycle)],
            "COURSE": [MessageHandler(Filters.text, Sell.sell_course)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"), Sell.sell_undo), CommandHandler('cancel', Sell.sell_undo)]
    )

    sell_my_items_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['my_items']}$"), Sell.sell_my_items)
    
    buy_search_by_name_handler = ConversationHandler(
        entry_points =[MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['search_by_name']}$"), Buy.buy_search_by_name)],
        states = {
            "DONE" : [MessageHandler(Filters.text, Buy.buy_search_by_name_done)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"),Buy.buy_search_by_name_undo), CommandHandler('cancel',Buy.buy_search_by_name_undo)]
    )
    
    buy_search_by_course_handler = ConversationHandler(
        entry_points =[MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['search_by_course']}$"), Buy.buy_search_by_course)],
        states = {
            "CYCLE" : [MessageHandler(Filters.text, Buy.buy_search_by_course_cycle)],
            "DONE" : [MessageHandler(Filters.text, Buy.buy_search_by_course_done)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"), Buy.buy_search_by_course_undo), CommandHandler('cancel',Buy.buy_search_by_course_undo)]
    )

    buy_last_added_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['last_added']}$"), Buy.buy_last_added)

    buy_chat_handler = CallbackQueryHandler(Buy.buy_chat,pattern=r"^chat$")

    # Navigation    
    navigation_prev_handler = CallbackQueryHandler(Navigation.navigation_prev,pattern=r"^prev$")
    navigation_next_handler = CallbackQueryHandler(Navigation.navigation_next,pattern=r"^next$")
    navigation_delete_handler = CallbackQueryHandler(Navigation.navigation_delete,pattern=r"^delete$")
    navigation_yes_handler = CallbackQueryHandler(Navigation.navigation_yes,pattern=r"yes")
    navigation_no_handler  = CallbackQueryHandler(Navigation.navigation_no,pattern=r"no")

    def add_test(update, context):
        try:            
            #session.query(Item).delete()
            session.add(Item(chat_id=123456781,title="Primo libro",photo='0',price='5.00',course="Agraria",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(chat_id=123456782,title="Secondo libro",photo='0',price='8.00',course="Biologia",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(chat_id=123456783,title="Terza dispensa",photo='0',price='10.00',course="Farmacia",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(chat_id=ADMIN_CHAT_ID,title="Quarto libro",photo='0',price='12.00',course="Matematica",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(chat_id=123456785,title="Quinta dispensa",photo='0',price='15.00',course="Psicologia",timestamp=int(time()),visible=True))
            session.commit()
            context.bot.send_message(chat_id=update.message.chat_id,text="Ho aggiunti gli item al db!")
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat_id,text=f"Errore: {e}")
    def set_section(update, context):
        context.user_data['section'] = "sell"
    add_test_handler = CommandHandler('add', add_test)
    set_section_handler = CommandHandler('section', set_section)
    
    # DISPATCHER
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(sell_handler)
    dispatcher.add_handler(buy_handler)
    dispatcher.add_handler(info_handler)
    dispatcher.add_handler(back_handler)
    dispatcher.add_handler(instruction_handler)
    dispatcher.add_handler(sell_new_item_handler)
    dispatcher.add_handler(sell_my_items_handler)
    dispatcher.add_handler(feedback_handler)
    dispatcher.add_handler(add_test_handler)
    dispatcher.add_handler(set_section_handler)
    dispatcher.add_handler(buy_last_added_handler)
    dispatcher.add_handler(buy_search_by_name_handler)
    dispatcher.add_handler(buy_search_by_course_handler)
    dispatcher.add_handler(buy_chat_handler)
    dispatcher.add_handler(navigation_prev_handler)
    dispatcher.add_handler(navigation_next_handler)
    dispatcher.add_handler(navigation_delete_handler)
    dispatcher.add_handler(navigation_yes_handler)
    dispatcher.add_handler(navigation_no_handler)

    # POLLING
    updater.start_polling()
    updater.idle()
    updater.stop()