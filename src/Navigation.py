# -*- coding: utf-8 -*-

import Keyboards
import json
import Database
from Settings import *
from telegram import InputMediaPhoto
from datetime import datetime

with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
    statements = json.load(lang_f)

def navigation_prev(update, context):
    if context.user_data['last_count'] == 0:
        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['no_prev_items'],cache_time=5)
    else:
        context.user_data['last_count'] -= 1
        prev_item  = context.user_data['last_items'][context.user_data['last_count']]

        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['callback_answers']['previous'])
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=prev_item.photo if not prev_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(prev_item,[context.user_data['last_count']+1, context.user_data['items_count']]),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if context.user_data['section'] == "sell" else Keyboards.NavigationChat)

def navigation_next(update, context):
    if context.user_data['last_count'] == context.user_data['items_count']-1:
        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['no_next_items'],cache_time=5)
    else:
        context.user_data['last_count'] += 1
        next_item = context.user_data['last_items'][context.user_data['last_count']]

        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['callback_answers']['next'])
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=next_item.photo if not next_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(next_item,[context.user_data['last_count']+1,context.user_data['items_count']]),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if context.user_data['section'] == "sell" else Keyboards.NavigationChat)


def navigation_delete(update, context):
    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=Keyboards.Confirm
    )
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=statements['callback_answers']['are_you_sure'],
        cache_time=0)

def navigation_yes(update, context):
    # BUG: last_count index error when deleting last item of my items menu
    item = context.user_data['last_items'][context.user_data['last_count']]
    db_item = Database.get_item_by_id(item.item_id)
    Database.session.delete(item)
    Database.session.commit()
    context.user_data['last_items'].remove(item)
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=f"{item.title}  🚮",
        cache_time=5)

    if context.user_data['items_count'] == 0:
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
        context.user_data['last_count'] -= 1
        prev_item  = context.user_data['last_items'][context.user_data['last_count']]
    
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=prev_item.photo if not prev_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(prev_item),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if context.user_data['items_count'] > 1 else Keyboards.OnlyDelete)


def navigation_no(update, context):
    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=Keyboards.NavigationDelete if context.user_data['items_count'] > 1 else Keyboards.OnlyDelete
    )
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=statements['callback_answers']['as_you_want'],
        cache_time=0)

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