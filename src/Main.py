# -*- coding: utf-8 -*-

import logging
import json
import Keyboards
from sys import exit
from re import search
from os.path import isfile as file_exists
from uuid import uuid1
from time import time
from datetime import datetime
from functools import wraps

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, asc

# Telegram Bot
from telegram import ReplyKeyboardMarkup
from telegram import ChatAction
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import Filters
from telegram.ext import Updater
from telegram import InputMediaPhoto

API_TOKEN = None
DB_FILE = "Database.db"
LANG = "IT" # [IT, EN, ES, DE]
IMG_NOT_AVAILABLE = None
ADMIN_CHAT_ID = None

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
        context.bot.send_message(chat_id=update.message.chat_id, 
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
        context.bot.send_message(chat_id=update.message.chat_id,
            text=statements['welcome'].replace("$$",update.message.chat.first_name),
            reply_markup=Keyboards.Start,
            parse_mode="Markdown")

# SELL
def sell(update, context):
    # Maybe this format is better?
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements["sell"],
        reply_markup=Keyboards.Sell,
        parse_mode="markdown")

@typing_action
def sell_title(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_title"], reply_markup=Keyboards.Undo, parse_mode="markdown")
    context.user_data['item_id'] = uuid1().hex
    return "TITLE"

@typing_action
def sell_price(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_undo"], reply_markup=Keyboards.Sell, parse_mode="markdown")
        context.user_data.clear()
        return ConversationHandler.END

    # Save title
    # Check for SQL Injection 
    context.user_data['title'] = update.message.text
    context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_price"], reply_markup=Keyboards.Price, parse_mode="markdown")
    return "PRICE"

@typing_action
def sell_photo(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_undo"], reply_markup=Keyboards.Sell, parse_mode="markdown")
        context.user_data.clear()
        return ConversationHandler.END

    if search(r"^[0-9]{1,3}(\,|.|$)[0-9]{0,2}(€){0,1}$", update.message.text):
        # Save price
        context.user_data['price'] = update.message.text.replace('€','').replace(',','.')
        context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_photo"], reply_markup=Keyboards.Skip, parse_mode="markdown")
        return "COURSE"
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_bad_price"], parse_mode="markdown")
        return "PRICE"

@typing_action
def sell_skip_photo(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_undo"], reply_markup=Keyboards.Sell, parse_mode="markdown")
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data['photo'] = '0'
    context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_skip_photo"], parse_mode="markdown")
    context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_courses"], reply_markup=Keyboards.Courses, parse_mode="markdown")
    return "DONE"

@typing_action
def sell_courses(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_undo"], reply_markup=Keyboards.Sell, parse_mode="markdown")
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data["photo"] = update.message.photo[len(update.message.photo)-1].file_id
    context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_courses"], reply_markup=Keyboards.Courses, parse_mode="markdown")
    return "DONE"

@typing_action
def sell_undo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_undo"], reply_markup=Keyboards.Sell, parse_mode="markdown")
    context.user_data.clear()
    return ConversationHandler.END

@typing_action
def sell_done(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_undo"], reply_markup=Keyboards.Sell, parse_mode="markdown")
        context.user_data.clear()
        return ConversationHandler.END

    if not update.message.text in statements['keyboards']['courses']:
        context.bot.send_message(chat_id=update.message.chat_id,text=statements["sell_wrong_course"],parse_mode="Markdown")
        return "DONE"
        
    context.user_data['course'] = update.message.text
    
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
    context.bot.send_message(chat_id=update.message.chat_id, text=statements["sell_done"], reply_markup=Keyboards.Sell, parse_mode="Markdown")
    
    item = get_item_by_id(context.user_data['item_id'])
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=item.photo if not item.photo == '0' else IMG_NOT_AVAILABLE,
        caption=build_item_caption(item),
        reply_markup=Keyboards.build_my_items_keyboard(item.item_id),
        parse_mode="Markdown")

    return ConversationHandler.END

def sell_my_items(update, context):
    # Prendere solo il primo
    my_items = get_my_items(update.message.chat_id)
    if not my_items:
        context.bot.send_message(chat_id=update.message.chat_id,text=statements['sell_empty_my_items'],parse_mode="Markdown")
    else:
        context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['sell_count_my_items_many'].replace('$$',str(len(my_items))) if len(my_items) > 1 else statements['sell_count_my_items_one'],
            parse_mode="Markdown")
        
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=my_items[0].photo if not my_items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(my_items[0]),
            reply_markup=Keyboards.build_my_items_keyboard(my_items[0].item_id),
            parse_mode="Markdown")

def sell_my_items_prev(update, context):
    prev_item = get_my_items_prev(update.callback_query.data[5:])
    if prev_item:
        context.bot.send_chat_action(chat_id=update.callback_query.message.chat_id, action=ChatAction.UPLOAD_PHOTO)
        context.bot.answer_callback_query(update.callback_query.id,text=statements['callback_answers']['previous'])
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=prev_item.photo if not prev_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(prev_item),
                parse_mode="Markdown"),
            reply_markup=Keyboards.build_my_items_keyboard(prev_item.item_id))
    else:
        context.bot.answer_callback_query(update.callback_query.id,text=statements['sell_cb_no_prev_items'],cache_time=5)

def sell_my_items_next(update, context):
    next_item = get_my_items_next(update.callback_query.data[5:])
    if next_item:
        context.bot.send_chat_action(chat_id=update.callback_query.message.chat_id, action=ChatAction.UPLOAD_PHOTO)
        context.bot.answer_callback_query(update.callback_query.id,text=statements['callback_answers']['next'])    
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=next_item.photo if not next_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(next_item),
                parse_mode="Markdown"),
            reply_markup=Keyboards.build_my_items_keyboard(next_item.item_id))
    else:
        context.bot.answer_callback_query(update.callback_query.id,text=statements['sell_cb_no_next_items'],cache_time=5)

def sell_my_items_delete(update, context):
    context.bot.send_chat_action(chat_id=update.callback_query.message.chat_id, action=ChatAction.TYPING)
    item = get_item_by_id(update.callback_query.data[7:])
    #title = item.title
    session.delete(item)
    session.commit()
    context.bot.answer_callback_query(update.callback_query.id,text=f"{item.title}  🚮",cache_time=10)

    items = get_my_items(update.callback_query.message.chat_id)
    if items:
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=items[0].photo if not items[0].photo== '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(items[0]),
                parse_mode="Markdown"),
            reply_markup=Keyboards.build_my_items_keyboard(items[0].item_id))
    else:
        # Maybe another method?
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,message_id=update.callback_query.message.message_id)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id,text=statements['sell_empty_my_items'],parse_mode="Markdown")
      
# BUY
def buy(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=statements['buy'],reply_markup=Keyboards.Buy,parse_mode="Markdown")

def buy_search_by_name(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=statements['buy_search_by_name'],parse_mode="Markdown")
    return "DONE"

def buy_search_by_name_done(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(chat_id=update.message.chat_id,text=statements['buy_search_by_name_undo'],reply_markup=Keyboards.Buy,parse_mode="markdown")
        return ConversationHandler.END

    if len(update.message.text) < 4:
        context.bot.send_message(chat_id=update.message.chat_id,text=statements['buy_search_by_name_more_char'],parse_mode="Markdown")
        return "DONE"

    # EH 

    items = get_items_from_db(update.message.text)

    if items:
        context.user_data['last_query'] = update.message.text
        context.bot.send_message(chat_id=update.message.chat_id,text=statements['buy_search_by_name_done'],reply_markup=Keyboards.Buy,parse_mode="Markdown")
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=items[0].photo if not items[0].photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(items[0]),
            reply_markup=Keyboards.build_items_keyboard(items[0].item_id),
            parse_mode="Markdown")
    else:
        context.bot.send_message(chat_id=update.message.chat_id,text=statements['buy_search_by_name_no_result'],reply_markup=Keyboards.Buy, parse_mode="Markdown")

    return ConversationHandler.END

def buy_search_by_name_undo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=statements['buy_search_by_name_undo'],reply_markup=Keyboards.Buy,parse_mode="Markdown")


@photo_action
def buy_last_added(update, context):
    items = get_last_added()
    for item in items:
        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=item.photo if not item.photo == '0' else IMG_NOT_AVAILABLE,
            caption=build_item_caption(item),
            #reply_markup=Keyboards.build_my_items_keyboard(item.item_id),
            parse_mode="Markdown")

# INFO
def info(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=statements['info'],parse_mode="Markdown")

# BACK
def back(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=statements['main_menu'],reply_markup=Keyboards.Start,parse_mode="Markdown")

# FEEDBACK
def feedback(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=statements['feedback'],reply_markup=Keyboards.Undo,parse_mode="Markdown")
    return "DONE"

def feedback_done(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(chat_id=update.message.chat_id,text=statements["feedback_undo"],reply_markup=Keyboards.Start,parse_mode="markdown")
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

    context.bot.send_message(chat_id=update.message.chat_id,text=statements['feedback_done'],reply_markup=Keyboards.Start,parse_mode="Markdown")
    return ConversationHandler.END


def feedback_undo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=statements['feedback_undo'],reply_markup=Keyboards.Start,parse_mode="Markdown")

# UTILITY

def count_my_items(chat_id):
    return len(get_my_items(chat_id))

def get_my_items(chat_id):
    return session.query(Item).filter_by(chat_id=chat_id).order_by(asc(Item.timestamp)).all()

def get_my_items_prev(item_id):
    return session.query(Item).filter(Item.item_id < item_id).order_by(desc(Item.timestamp)).first()

# Note: Invertire asc e desc tra queste due righe per visualizzare 
# rispettivamente l'ultimo ed il primo nei miei annunci come primo risultato

def get_my_items_next(item_id):
    return session.query(Item).filter(Item.item_id > item_id).order_by(asc(Item.timestamp)).first()

def build_item_caption(item):
    fromts = datetime.fromtimestamp(item.timestamp)
    date = "{0}/{1}/{2}".format('%02d' % fromts.day, '%02d' % fromts.month, fromts.year)
    return f"*📌 {statements['caption']['title']}:* {item.title}\n" \
        f"*💵 {statements['caption']['price']}:* {item.price}€\n" \
        f"*🎓 {statements['caption']['course']}:* {item.course}\n" \
        f"*🗓 {statements['caption']['posted']}:* {date}"

def get_item_by_id(item_id):
    return session.query(Item).filter_by(item_id=item_id).first()

def get_items_from_db(query):
    return session.query(Item).filter(Item.title.like(query)).all()

def get_last_added():
    return session.query(Item).order_by(desc(Item.timestamp)).limit(3).all()

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
    
    with open(f"{LANG}.lang", 'r') as lang_file:
        statements = json.load(lang_file)

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
    info_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['info']}$"), info)
    back_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['back']['back']}$"), back)
    
    sell_conversation_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['new_item']}$"), sell_title)],
        states = {
            # Si potrebbe aggiungere un handler per Annulla direttamente qui
            "TITLE":  [MessageHandler(Filters.text, sell_price)],
            "PRICE":  [MessageHandler(Filters.text, sell_photo)],
            "COURSE": [MessageHandler(Filters.regex(rf"^{statements['keyboards']['skip']['skip']}$"), sell_skip_photo),
                        MessageHandler(Filters.photo, sell_courses)],
            "DONE":   [MessageHandler(Filters.text, sell_done)],
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['abort']['abort']}$"), sell_undo), CommandHandler('cancel', sell_undo)]
    )

    sell_my_items_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['my_items']}$"), sell_my_items)
    sell_my_items_prev_handler = CallbackQueryHandler(sell_my_items_prev,pattern=r"^prev_")
    sell_my_items_next_handler = CallbackQueryHandler(sell_my_items_next,pattern=r"^next_")
    sell_my_items_delete_handler = CallbackQueryHandler(sell_my_items_delete,pattern=r"^delete_")

    buy_search_by_name_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['search_by_name']}$"), buy_search_by_name)
    buy_last_added_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['last_added']}$"), buy_last_added)

    def add_test(update, context):
        try:            
            session.query(Item).delete()
            session.add(Item(item_id="13ead83ce55811e984af48452083e01e",chat_id=ADMIN_CHAT_ID,title="Primo libro",photo='0',price='5.00',course="Agraria",timestamp=int(time()),visible=True))
            session.add(Item(item_id="1beadae6e55811e984af48452083e01e",chat_id=ADMIN_CHAT_ID,title="Secondo libro",photo='0',price='8.00',course="Biologia",timestamp=int(time()),visible=True))
            session.add(Item(item_id="2e497d96e55811e984af48452083e01e",chat_id=ADMIN_CHAT_ID,title="Terza dispensa",photo='0',price='10.00',course="Farmacia",timestamp=int(time()),visible=True))
            session.add(Item(item_id="357bb0ace55811e984af48452083e01e",chat_id=ADMIN_CHAT_ID,title="Quarto libro",photo='0',price='12.00',course="Matematica",timestamp=int(time()),visible=True))
            session.add(Item(item_id="469c5d00e55811e984af48452083e01e",chat_id=ADMIN_CHAT_ID,title="Quinta dispensa",photo='0',price='15.00',course="Psicologia",timestamp=int(time()),visible=True))
            context.bot.send_message(chat_id=update.message.chat_id,text="Ho aggiunti gli item al db!")
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat_id,text=f"Errore: {e}")

    add_test_handler = CommandHandler('add', add_test)

    # DISPATCHER
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(sell_handler)
    dispatcher.add_handler(buy_handler)
    dispatcher.add_handler(info_handler)
    dispatcher.add_handler(back_handler)
    dispatcher.add_handler(sell_conversation_handler)
    dispatcher.add_handler(sell_my_items_handler)
    dispatcher.add_handler(sell_my_items_prev_handler)
    dispatcher.add_handler(sell_my_items_next_handler)
    dispatcher.add_handler(sell_my_items_delete_handler)
    dispatcher.add_handler(feedback_handler)
    dispatcher.add_handler(add_test_handler)
    dispatcher.add_handler(buy_last_added_handler)
    dispatcher.add_handler(buy_search_by_name_handler)

    # POLLING
    updater.start_polling()
    updater.idle()
    updater.stop()