# -*- coding: utf-8 -*-

import json
import logging
import Keyboards

from sys import exit
from os import getenv
from re import search
from time import time
from time import sleep
from uuid import uuid1
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
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

# Load environment
load_dotenv()

API_TOKEN = getenv("API_TOKEN")
DB_FILE = getenv("DB_FILE")
LANG_FILE = getenv("LANG_FILE") # [IT, EN, ES, DE]
IMG_NOT_AVAILABLE = getenv("IMG_NOT_AVAILABLE")
ADMIN_CHAT_ID = getenv("ADMIN_CHAT_ID")

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

# SELL
def sell(update, context):
    context.user_data['section'] = "sell"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements["sell"],
        reply_markup=Keyboards.Sell,
        parse_mode="markdown")

def sell_new_item(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements["sell_title"],
        reply_markup=Keyboards.Undo,
        parse_mode="markdown")
    context.user_data['item_id'] = uuid1().hex
    return "TITLE"

def sell_title(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_undo"],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        context.user_data['item_id'] = None
        return ConversationHandler.END

    # Check for SQL Injection 
    context.user_data['title'] = update.message.text
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements["sell_price"],
        reply_markup=Keyboards.Price,
        parse_mode="markdown")
    return "PRICE"

def sell_price(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_undo"],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        context.user_data['item_id'] = None
        context.user_data['title'] = None
        return ConversationHandler.END

    if search(r"^[0-9]{1,3}(\,|.|$)[0-9]{0,2}(€){0,1}$", update.message.text):
        
        # Replace euro symbol, then replace comma with period
        price = update.message.text.replace('€','').replace(',','.')
        
        # No decimal digit, no (.), optional (€) (eg. 7€, 8, 123€, 23)
        if search(r"^[0-9]{1,3}(€){0,1}$", price):
            price = f"{price}.00"
        # Only one decimal digit imply 0 as second decimal digit
        elif search(r"^[0-9]{1,3}\.[0-9]{1}(€){0,1}$", price):
            price = f"{price}0"

        # Save price
        context.user_data['price'] = price
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_photo"],
            reply_markup=Keyboards.Skip,
            parse_mode="markdown")
        return "PHOTO"
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_bad_price"],
            parse_mode="markdown")
        return "PRICE"

def sell_photo(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_undo"],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        context.user_data['item_id'] = None
        context.user_data['title'] = None
        context.user_data['price'] = None
        return ConversationHandler.END

    if update.message.text and update.message.text == statements['keyboards']['skip']['skip']:
        context.user_data['photo'] = '0'
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_skip_photo"],
            parse_mode="markdown")
    elif update.message.photo:
        context.user_data["photo"] = update.message.photo[len(update.message.photo)-1].file_id
    else: # No "Skip", no photo
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_photo_wrong"],
            parse_mode="markdown")
        return "PHOTO"

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements["sell_cycle"],
        reply_markup=Keyboards.Cycle,
        parse_mode="markdown")
    return "CYCLE"

def sell_cycle(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_undo"],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        context.user_data['item_id'] = None
        context.user_data['title'] = None
        context.user_data['price'] = None
        context.user_data['photo'] = None
        return ConversationHandler.END

    if update.message.text == statements['keyboards']['first_cycle'] \
        or update.message.text == statements['keyboards']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_course'],
            reply_markup=Keyboards.FirstCycle if update.message.text == statements['keyboards']['first_cycle'] else Keyboards.LongCycle,
            parse_mode="markdown")
        return "COURSE"
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_cycle_wrong'],
            reply_markup=Keyboards.Cycle,
            parse_mode="markdown")
        return "CYCLE"   

@typing_action
def sell_course(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["sell_undo"],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        context.user_data['item_id'] = None
        context.user_data['title'] = None
        context.user_data['price'] = None
        context.user_data['photo'] = None
        return ConversationHandler.END

    if update.message.text == statements['keyboards']['first_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_course'],
            reply_markup=Keyboards.FirstCycle,
            parse_mode="markdown")
        return "COURSE"
    
    elif update.message.text == statements['keyboards']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_course'],
            reply_markup=Keyboards.LongCycle,
            parse_mode="markdown")
        return "COURSE"

    if not update.message.text in statements['keyboards']['courses']['first_cycle'] \
        and not update.message.text in statements['keyboards']['courses']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_course_wrong'],
            parse_mode="markdown")
        return "COURSE"

    # Check SQLi 
    context.user_data['course'] = update.message.text

    # Done
    # Check for SQL Injection 
    session.add(
        Item(
            item_id   = context.user_data['item_id'],
            chat_id   = update.message.chat_id,
            title     = context.user_data['title'],
            photo     = context.user_data['photo'],
            price     = context.user_data['price'],
            course    = context.user_data['course'],
            timestamp = int(time()),
            visible = True
        )
    )
    session.commit()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements["sell_done"],
        reply_markup=Keyboards.Sell,
        parse_mode="Markdown")
    
    # Preview
    item = get_item_by_id(context.user_data['item_id'])
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=item.photo if not item.photo == '0' else IMG_NOT_AVAILABLE,
        caption=build_item_caption(item),
        reply_markup=Keyboards.OnlyDelete,
        parse_mode="Markdown")

    return ConversationHandler.END

def sell_undo(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements["sell_undo"],
        reply_markup=Keyboards.Sell,
        parse_mode="markdown")
    context.user_data['item_id'] = None
    context.user_data['title'] = None
    context.user_data['price'] = None
    context.user_data['photo'] = None
    context.user_data['course'] = None
    return ConversationHandler.END

@typing_action
def sell_my_items(update, context):
    my_items = get_my_items(update.message.chat_id)
    if not my_items:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_empty_my_items'],
            parse_mode="Markdown")
    else:
        context.user_data['last_items'] = my_items
        context.user_data['last_count'] = 0
        my_items_count = len(my_items)
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_count_my_items_many'].replace('$$',str(my_items_count)) if my_items_count > 1 else statements['sell_count_my_items_one'],
            parse_mode="Markdown")
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=my_items[0].photo if not my_items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(my_items[0]),
            reply_markup=Keyboards.NavigationDelete if my_items_count > 1 else Keyboards.OnlyDelete,
            parse_mode="Markdown")

# BUY
def buy(update, context):
    context.user_data['section'] = "buy"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['buy'],
        reply_markup=Keyboards.Buy,
        parse_mode="Markdown")

def buy_search_by_name(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['buy_search_by_name'],
        reply_markup=Keyboards.Undo,
        parse_mode="Markdown")
    return "DONE"

def buy_search_by_name_done(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_name_undo'],
            reply_markup=Keyboards.Buy,
            parse_mode="markdown")
        return ConversationHandler.END

    if len(update.message.text) < 4:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_name_more_char'],
            parse_mode="Markdown")
        return "DONE"

    items = get_items_by_name(update.message.chat_id, update.message.text)

    if items:
        #context.user_data['last_query'] = update.message.text
        context.user_data['last_items'] = items
        context.user_data['last_count'] = 0
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_name_done'].replace('$$',str(len(items))),
            reply_markup=Keyboards.Buy,
            parse_mode="Markdown")
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=items[0].photo if not items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(items[0]),
            reply_markup=Keyboards.NavigationChat if len(items) > 1 else Keyboards.OnlyChat,
            parse_mode="Markdown")
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_name_no_result'],
            reply_markup=Keyboards.Buy,
            parse_mode="Markdown")
        #return "DONE"

    return ConversationHandler.END

def buy_search_by_name_undo(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['buy_search_by_name_undo'],
        reply_markup=Keyboards.Buy,
        parse_mode="Markdown")

def buy_search_by_course(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['buy_search_by_course'],
        reply_markup=Keyboards.Cycle,
        parse_mode="Markdown")
    return "CYCLE"

def buy_search_by_course_cycle(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_course_undo'],
            reply_markup=Keyboards.Buy,
            parse_mode="markdown")
        return ConversationHandler.END

    if update.message.text == statements['keyboards']['first_cycle'] \
        or update.message.text == statements['keyboards']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_course_done'],
            reply_markup=Keyboards.FirstCycle if update.message.text == statements['keyboards']['first_cycle'] else Keyboards.LongCycle,
            parse_mode="markdown")
        return "DONE"
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_course_wrong'],
            reply_markup=Keyboards.Cycle,
            parse_mode="markdown")
        return "CYCLE"

def buy_search_by_course_done(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_course_undo'],
            reply_markup=Keyboards.Buy,
            parse_mode="markdown")
        return ConversationHandler.END

    if update.message.text == statements['keyboards']['first_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_course_first'],
            reply_markup=Keyboards.FirstCycle,
            parse_mode="markdown")
        return "DONE"
    elif update.message.text == statements['keyboards']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_course_long'],
            reply_markup=Keyboards.LongCycle,
            parse_mode="markdown")
        return "DONE"

    if not update.message.text in statements['keyboards']['courses']['first_cycle'] \
        and not update.message.text in statements['keyboards']['courses']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_course_invalid_course'],
            reply_markup=Keyboards.Cycle,
            parse_mode="markdown")
        return "CYCLE"
    
    items = get_items_by_course(update.message.chat_id, update.message.text)

    if items:
        context.user_data['last_items'] = items
        context.user_data['last_count'] = 0
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_name_done'].replace('$$',str(len(items))),
            reply_markup=Keyboards.Buy,
            parse_mode="Markdown")
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=items[0].photo if not items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(items[0]),
            reply_markup=Keyboards.NavigationChat if len(items) > 1 else Keyboards.OnlyChat,
            parse_mode="Markdown")
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_course_no_result'],
            reply_markup=Keyboards.Buy,
            parse_mode="Markdown")
        #return "DONE"

    return ConversationHandler.END

def buy_search_by_course_undo(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['buy_search_by_course_undo'],
        reply_markup=Keyboards.Buy,
        parse_mode="Markdown")

def buy_last_added(update, context):
    items = get_last_added(update.message.chat_id)
    if items:
        context.user_data['last_items'] = items
        context.user_data['last_count'] = 0

        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=items[0].photo if not items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(items[0]),
            reply_markup=Keyboards.Navigation,
            parse_mode="Markdown")
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_last_added_no_result'],
            reply_markup=Keyboards.Buy,
            parse_mode="Markdown")

def buy_chat(update, context):
    seller_chat_id = context.user_data['last_items'][context.user_data['last_count']].chat_id
    seller_username = f"@{get_username_by_chatid(seller_chat_id)[0]}"
    context.bot.edit_message_caption(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        caption=f"{update.callback_query.message.caption}\n👤 {seller_username}",
        reply_markup=Keyboards.Navigation,
        parse_mode="markdown"
    )
    context.bot.answer_callback_query(
        update.callback_query.id,
        text="username visualizzato",
        cache_time=5
    )

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
        context.user_data['last_count'] = 0
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['main_menu'],
            reply_markup=Keyboards.Start,
            parse_mode="Markdown")

# FEEDBACK
def feedback(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['feedback'],
        reply_markup=Keyboards.Undo,
        parse_mode="Markdown")
    return "DONE"

def feedback_done(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["feedback_undo"],
            reply_markup=Keyboards.Start,
            parse_mode="markdown")
        return ConversationHandler.END

    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=statements['feedback_received'] \
            .replace('$$',str(update.message.chat_id),1) \
            .replace('$$',update.message.chat.username, 1) \
            .replace('$$',update.message.chat.first_name, 1),
        parse_mode="Markdown"
    )

    context.bot.forward_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['feedback_done'],
        reply_markup=Keyboards.Start,
        parse_mode="Markdown")
    return ConversationHandler.END

def feedback_undo(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['feedback_undo'],
        reply_markup=Keyboards.Start,
        parse_mode="Markdown")

# UTILITY

def count_my_items(chat_id):
    return len(get_my_items(chat_id))

def get_my_items(chat_id):
    return session.query(Item).filter_by(chat_id=chat_id).order_by(desc(Item.timestamp)).all()

def build_item_caption(item):
    fromts = datetime.fromtimestamp(item.timestamp)
    date = "{0}/{1}/{2}".format('%02d' % fromts.day, '%02d' % fromts.month, fromts.year)
    return f"*📌 {statements['caption']['title']}:* {item.title}\n" \
        f"*💵 {statements['caption']['price']}:* {item.price}€\n" \
        f"*🎓 {statements['caption']['course']}:* {item.course}\n" \
        f"*🗓 {statements['caption']['posted']}:* {date}"

def get_item_by_id(item_id):
    return session.query(Item).filter_by(item_id=item_id).first()

def get_items_by_name(chat_id, query):
    return session.query(Item).filter(Item.chat_id != chat_id).filter(Item.title.like(f"%{query}%")).all()

def get_items_by_course(chat_id, course):
    return session.query(Item).filter(Item.chat_id != chat_id).filter(Item.course == course).order_by(desc(Item.timestamp)).all()

def get_last_added(chat_id):
    return session.query(Item).filter(Item.chat_id != chat_id).order_by(desc(Item.timestamp)).limit(3).all()

def get_username_by_chatid(chat_id):
    return session.query(User.username).filter(User.chat_id == chat_id).first()

def navigation_prev(update, context):
    if context.user_data['last_count'] == 0:
        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['no_prev_items'],cache_time=5)
    else:
        last_count = context.user_data['last_count']
        prev_item  = context.user_data['last_items'][last_count-1]
        
        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['callback_answers']['previous'])
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=prev_item.photo if not prev_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(prev_item),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if context.user_data['section'] == "sell" else Keyboards.NavigationChat)
        context.user_data['last_count'] -= 1

def navigation_next(update, context):
    if context.user_data['last_count'] == len(context.user_data['last_items'])-1:
        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['no_next_items'],cache_time=5)
    else:
        last_count = context.user_data['last_count']
        next_item = context.user_data['last_items'][last_count+1]
        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['callback_answers']['next'])
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=next_item.photo if not next_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(next_item),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if context.user_data['section'] == "sell" else Keyboards.NavigationChat)

        context.user_data['last_count'] += 1

def navigation_delete(update, context):
    item = context.user_data['last_items'][context.user_data['last_count']]
    db_item = get_item_by_id(item.item_id)
    session.delete(item)
    session.commit()
    context.user_data['last_items'].remove(item)
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=f"{item.title}  🚮",
        cache_time=10)

    if len(context.user_data['last_items']) == 0:
        context.user_data['last_items'] = None
        context.user_data['last_count'] = None
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=statements['sell_deleted_last_item'],
            parse_mode="Markdown")
    else:
        last_count = context.user_data['last_count']
        prev_item  = context.user_data['last_items'][last_count-1]
    
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=prev_item.photo if not prev_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(prev_item),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if len(context.user_data['last_items']) > 1 else Keyboards.OnlyDelete)

        context.user_data['last_count'] -= 1

if __name__ == "__main__":

    # INIT
    if not API_TOKEN: exit("Invalid token!")
    if not DB_FILE: DB_FILE = "Database.db"
    
    # DATABASE
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Base = declarative_base()

    class User(Base):
        __tablename__ = "Users"
        
        chat_id    = Column(Integer, primary_key=True)
        username   = Column(String)
        first_name = Column(String)

        def __repr__(self):
            return "<User(chat_id='%s', username='%s', first_name='%s')>" % \
                    (self.chat_id, self.username, self.first_name)

    class Item(Base):
        __tablename__ = "Items"

        item_id   = Column(String(32), primary_key=True)
        chat_id   = Column(Integer)
        title     = Column(String)
        photo     = Column(String(128), default='0')
        price     = Column(String(8))
        course    = Column(String(128))
        timestamp = Column(Integer)
        visible   = Column(Boolean, default=True)

        def __repr__(self):
            return "<Item(item_id='%s', chat_id='%s',title='%s',photo='%s',price='%s',course='%s',visible='%s')" % \
                (self.item_id, self.chat_id, self.title, self.photo, self.price, self.course, self.visible)

    if not file_exists(DB_FILE): Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    # UPDATER, DISPATCHER, LOGGING AND LANGUAGE
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(
        level=logging.DEBUG, # DEBUG
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
        statements = json.load(lang_f)

    # HANDLERS
    start_handler = CommandHandler('start', start)
    feedback_handler = ConversationHandler(
        entry_points = [CommandHandler('feedback', feedback)],
        states = {
            "DONE": [MessageHandler(Filters.text, feedback_done)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"), feedback_undo)]
    )

    sell_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['sell']}$"), sell)
    buy_handler   = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['buy']}$"), buy)
    info_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['info']}$"), information)
    back_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['back']['back']}$"), back)
    instruction_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['instructions']}$"), instructions)

    sell_new_item_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['new_item']}$"), sell_new_item)],
        states = {
            "TITLE":  [MessageHandler(Filters.text, sell_title)],
            "PRICE":  [MessageHandler(Filters.text, sell_price)],
            "PHOTO":  [MessageHandler(Filters.photo, sell_photo),
                       MessageHandler(Filters.regex(rf"^{statements['keyboards']['skip']['skip']}$"), sell_photo)],
            "CYCLE":  [MessageHandler(Filters.text, sell_cycle)],
            "COURSE": [MessageHandler(Filters.text, sell_course)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"), sell_undo), CommandHandler('cancel', sell_undo)]
    )

    sell_my_items_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['my_items']}$"), sell_my_items)
    
    buy_search_by_name_handler = ConversationHandler(
        entry_points =[MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['search_by_name']}$"), buy_search_by_name)],
        states = {
            "DONE" : [MessageHandler(Filters.text, buy_search_by_name_done)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"),buy_search_by_name_undo), CommandHandler('cancel',buy_search_by_name_undo)]
    )
    
    buy_search_by_course_handler = ConversationHandler(
        entry_points =[MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['search_by_course']}$"), buy_search_by_course)],
        states = {
            "CYCLE" : [MessageHandler(Filters.text, buy_search_by_course_cycle)],
            "DONE" : [MessageHandler(Filters.text, buy_search_by_course_done)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"), buy_search_by_course_undo), CommandHandler('cancel',buy_search_by_course_undo)]
    )

    buy_last_added_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['last_added']}$"), buy_last_added)

    buy_chat_handler = CallbackQueryHandler(buy_chat,pattern=r"^chat$")

    # Navigation    
    navigation_prev_handler = CallbackQueryHandler(navigation_prev,pattern=r"^prev$")
    navigation_next_handler = CallbackQueryHandler(navigation_next,pattern=r"^next$")
    navigation_delete_handler = CallbackQueryHandler(navigation_delete,pattern=r"^delete$")

    def add_test(update, context):
        try:            
            session.query(Item).delete()
            session.add(Item(item_id="13ead83ce55811e984af48452083e01e",chat_id=123456781,title="Primo libro",photo='0',price='5.00',course="Agraria",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(item_id="1beadae6e55811e984af48452083e01e",chat_id=123456782,title="Secondo libro",photo='0',price='8.00',course="Biologia",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(item_id="2e497d96e55811e984af48452083e01e",chat_id=123456783,title="Terza dispensa",photo='0',price='10.00',course="Farmacia",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(item_id="357bb0ace55811e984af48452083e01e",chat_id=ADMIN_CHAT_ID,title="Quarto libro",photo='0',price='12.00',course="Matematica",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(item_id="469c5d00e55811e984af48452083e01e",chat_id=123456785,title="Quinta dispensa",photo='0',price='15.00',course="Psicologia",timestamp=int(time()),visible=True))
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

    # POLLING
    updater.start_polling()
    updater.idle()
    updater.stop()