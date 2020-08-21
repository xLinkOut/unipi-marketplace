# -*- coding: utf-8 -*-

import Keyboards

from Settings import *
from Database import session, User, Item

# START
def start(update, context):
    if session.query(User).filter_by(chat_id=update.message.chat_id).first():
        # User already exists
        context.bot.send_message(
            chat_id=update.message.chat_id, 
            text=statements['menu']['welcome_back'].replace("$$",update.message.chat.first_name), 
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
            text=statements['menu']['welcome'].replace("$$",update.message.chat.first_name),
            reply_markup=Keyboards.Start,
            parse_mode="Markdown")


# INSTRUCTIONS
def instructions(update, context):
    if context.user_data['section'] == "sell":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['instructions'],
            parse_mode="Markdown")
    elif context.user_data['section'] == "buy":
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy']['instructions'],
            parse_mode="Markdown")

# INFORMATION
def information(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['menu']['information'],
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
            text=statements['menu']['main_menu'],
            reply_markup=Keyboards.Start,
            parse_mode="Markdown")

    