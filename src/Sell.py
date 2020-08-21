# -*- coding: utf-8 -*-
import Database
import Keyboards
import json
from Settings import *
from re import search
from time import time
from datetime import datetime
from Misc import typing_action
from telegram.ext import ConversationHandler
from Misc import build_item_caption

with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
    statements = json.load(lang_f)

# SELL
def sell(update, context):
    context.user_data['section'] = "sell"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['menu']['sell'],
        reply_markup=Keyboards.Sell,
        parse_mode="markdown")

def new_item(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['sell']['new_item']['title'],
        reply_markup=Keyboards.Undo,
        parse_mode="markdown")
    return "TITLE"

def title(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['undo'],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        return ConversationHandler.END

    # Check for SQL Injection 
    context.user_data['title'] = update.message.text
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['sell']['new_item']['price'],
        reply_markup=Keyboards.Price,
        parse_mode="markdown")
    return "PRICE"

def price(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['undo'],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
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
            text=statements['sell']['new_item']['photo'],
            reply_markup=Keyboards.Skip,
            parse_mode="markdown")
        return "PHOTO"
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['bad_price'],
            parse_mode="markdown")
        return "PRICE"

def photo(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['undo'],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        context.user_data['title'] = None
        context.user_data['price'] = None
        return ConversationHandler.END

    if update.message.text and update.message.text == statements['keyboards']['skip']['skip']:
        context.user_data['photo'] = '0'
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['skip_photo'],
            parse_mode="markdown")
    elif update.message.photo:
        context.user_data["photo"] = update.message.photo[len(update.message.photo)-1].file_id
    else: # No "Skip", no photo
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['photo_wrong'],
            parse_mode="markdown")
        return "PHOTO"

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['sell']['new_item']['cycle'],
        reply_markup=Keyboards.Cycle,
        parse_mode="markdown")
    return "CYCLE"

def cycle(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['undo'],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        context.user_data['title'] = None
        context.user_data['price'] = None
        context.user_data['photo'] = None
        return ConversationHandler.END

    if update.message.text == statements['keyboards']['first_cycle'] \
        or update.message.text == statements['keyboards']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['course'],
            reply_markup=Keyboards.FirstCycle if update.message.text == statements['keyboards']['first_cycle'] else Keyboards.LongCycle,
            parse_mode="markdown")
        return "COURSE"
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['cycle_wrong'],
            reply_markup=Keyboards.Cycle,
            parse_mode="markdown")
        return "CYCLE"   

@typing_action
def course(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['undo'],
            reply_markup=Keyboards.Sell,
            parse_mode="markdown")
        context.user_data['title'] = None
        context.user_data['price'] = None
        context.user_data['photo'] = None
        return ConversationHandler.END

    if update.message.text == statements['keyboards']['first_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['course'],
            reply_markup=Keyboards.FirstCycle,
            parse_mode="markdown")
        return "COURSE"
    
    elif update.message.text == statements['keyboards']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['course'],
            reply_markup=Keyboards.LongCycle,
            parse_mode="markdown")
        return "COURSE"

    if not update.message.text in statements['keyboards']['courses']['first_cycle'] \
        and not update.message.text in statements['keyboards']['courses']['long_cycle']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['new_item']['course_wrong'],
            parse_mode="markdown")
        return "COURSE"

    # Check SQLi 
    context.user_data['course'] = update.message.text

    # Done
    # Check for SQL Injection
    new_item = Database.Item(
            chat_id   = update.message.chat_id,
            title     = context.user_data['title'],
            photo     = context.user_data['photo'],
            price     = context.user_data['price'],
            course    = context.user_data['course'],
            timestamp = int(time()),
            visible = True
        ) 
    Database.session.add(new_item)
    Database.session.commit()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['sell']['new_item']['done'],
        reply_markup=Keyboards.Sell,
        parse_mode="Markdown")
    
    # Preview
    item = Database.get_item_by_id(new_item.item_id)
    context.user_data['last_items'] = [item]
    context.user_data['last_count'] = 0
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=item.photo if not item.photo == '0' else IMG_NOT_AVAILABLE,
        caption=build_item_caption(item),
        reply_markup=Keyboards.OnlyDelete,
        parse_mode="Markdown")

    context.user_data['title']   = None
    context.user_data['photo']   = None
    context.user_data['price']   = None
    context.user_data['course']  = None    

    return ConversationHandler.END

def undo(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['sell']['new_item']['undo'],
        reply_markup=Keyboards.Sell,
        parse_mode="markdown")
    context.user_data['title'] = None
    context.user_data['price'] = None
    context.user_data['photo'] = None
    context.user_data['course'] = None
    return ConversationHandler.END

@typing_action
def my_items(update, context):
    my_items = Database.get_my_items(update.message.chat_id)
    if not my_items:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['my_items']['empty_my_items'],
            parse_mode="Markdown")
    else:
        context.user_data['last_items'] = my_items
        context.user_data['items_count'] = len(my_items)
        context.user_data['last_count'] = 0

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell']['my_items']['count_my_items_many'].replace('$$',str(context.user_data['items_count'])) if context.user_data['items_count'] > 1 else statements['sell']['my_items']['count_my_items_one'],
            parse_mode="Markdown")
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=my_items[0].photo if not my_items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(my_items[0],[1,context.user_data['items_count']] if context.user_data['items_count'] > 1 else []),
            reply_markup=Keyboards.NavigationDelete if context.user_data['items_count'] > 1 else Keyboards.OnlyDelete,
            parse_mode="Markdown")
