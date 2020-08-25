# -*- coding: utf-8 -*-

from Settings import *
from os.path import isfile as file_exists
# SQLAlchemy
from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

# DATABASE
engine = create_engine(f"sqlite:///{DB_FILE}")
Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    
    chat_id    = Column(Integer, primary_key=True)
    username   = Column(String)
    first_name = Column(String)

    def __repr__(self):
        return f"<User(chat_id='{self.chat_id}', username='{self.username}', first_name='self.first_name')>"

class Item(Base):
    __tablename__ = "Items"

    item_id   = Column(Integer, primary_key=True)
    chat_id   = Column(Integer)
    title     = Column(String)
    photo     = Column(String(128), default='0')
    price     = Column(String(8))
    course    = Column(String(128))
    timestamp = Column(Integer)
    visible   = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Item(item_id='{self.item_id}', chat_id='{self.chat_id}', title='{self.title}', "\
            f"photo='{self.photo}', price='{self.price}', course='{self.course}',visible='{self.visible}')"

if not file_exists(DB_FILE): Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

def count_my_items(chat_id):
    return len(get_my_items(chat_id))

def get_my_items(chat_id):
    return session.query(Item).filter_by(chat_id=chat_id).order_by(desc(Item.timestamp)).all()

def get_item_by_id(item_id):
    return session.query(Item).filter_by(item_id=item_id).first()

def get_items_by_name(chat_id, query):
    return session.query(Item).filter(Item.chat_id != chat_id).filter(Item.title.like(f"%{query}%")).all()

def get_items_by_course(chat_id, course):
    return session.query(Item).filter(Item.chat_id != chat_id).filter(Item.course == course).order_by(desc(Item.timestamp)).all()

def get_last_added(chat_id):
    return session.query(Item).filter(Item.chat_id != chat_id).order_by(desc(Item.timestamp)).limit(3).all()

def get_user_by_chat_id(chat_id):
    return session.query(User).filter(User.chat_id == chat_id).first()
