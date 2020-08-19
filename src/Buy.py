# -*- coding: utf-8 -*-

import Database
import Keyboards
import json
from os import getenv
from dotenv import load_dotenv
from telegram.ext import ConversationHandler
from datetime import datetime

load_dotenv()
LANG_FILE = getenv("LANG_FILE") # [IT, EN, ES, DE]
IMG_NOT_AVAILABLE = getenv("IMG_NOT_AVAILABLE")

with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
    statements = json.load(lang_f)

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

    items = Database.get_items_by_name(update.message.chat_id, update.message.text)

    if items:
        #context.user_data['last_query'] = update.message.text
        context.user_data['last_items'] = items
        context.user_data['items_count'] = len(items)
        context.user_data['last_count'] = 0

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_name_done'].replace('$$',str(context.user_data['items_count'])),
            reply_markup=Keyboards.Buy,
            parse_mode="Markdown")
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=items[0].photo if not items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(items[0], [1,context.user_data['items_count']] if context.user_data['items_count'] > 1 else []),
            reply_markup=Keyboards.NavigationChat if context.user_data['items_count'] > 1 else Keyboards.OnlyChat,
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
    
    items = Database.get_items_by_course(update.message.chat_id, update.message.text)

    if items:
        context.user_data['last_items'] = items
        context.user_data['items_count'] = len(items)
        context.user_data['last_count'] = 0

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_search_by_name_done'].replace('$$',str(context.user_data['items_count'])),
            reply_markup=Keyboards.Buy,
            parse_mode="Markdown")
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=items[0].photo if not items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(items[0], [1,context.user_data['items_count']] if context.user_data['items_count'] > 1 else []),
            reply_markup=Keyboards.NavigationChat if context.user_data['items_count'] > 1 else Keyboards.OnlyChat,
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
    items = Database.get_last_added(update.message.chat_id)
    if items:
        context.user_data['last_items'] = items
        context.user_data['items_count'] = len(items)
        context.user_data['last_count'] = 0

        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=items[0].photo if not items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(items[0], [1,context.user_data['items_count']] if context.user_data['items_count'] > 1 else []),
            reply_markup=Keyboards.NavigationChat if context.user_data['items_count'] > 1 else Keyboards.OnlyChat,
            parse_mode="Markdown")
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['buy_last_added_no_result'],
            reply_markup=Keyboards.Buy,
            parse_mode="Markdown")

def buy_chat(update, context):
    seller_chat_id = context.user_data['last_items'][context.user_data['last_count']].chat_id
    user = Database.get_user_by_chat_id(seller_chat_id)
    seller_username = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={seller_chat_id})"

    context.bot.edit_message_caption(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        caption=f"{update.callback_query.message.caption}\n👤 {seller_username}",
        reply_markup=Keyboards.Navigation if len(context.user_data['last_items']) > 1 else None,
        parse_mode="markdown"
    )
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=statements['buy_username_chat'],
        cache_time=5
    )

def build_item_caption(item,page=[]):
    fromts = datetime.fromtimestamp(item.timestamp)
    date = "{0}/{1}/{2}".format('%02d' % fromts.day, '%02d' % fromts.month, fromts.year)
    caption = f"*{statements['caption']['title']}:* {item.title}\n" \
            f"*{statements['caption']['price']}:* {item.price}€\n" \
            f"*{statements['caption']['course']}:* {item.course}\n" \
            f"*{statements['caption']['posted']}:* {date}"
    if page:
        return f"*{statements['caption']['page']}:* {page[0]}/{page[1]}\n{caption}"
    else: 
        return caption