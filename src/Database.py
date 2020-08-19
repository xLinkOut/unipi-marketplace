# -*- coding: utf-8 -*-

from os import getenv
from dotenv import load_dotenv
from os.path import isfile as file_exists

# SQLAlchemy
from sqlalchemy import desc, asc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Boolean, text

# Load environment
load_dotenv()
DB_FILE = getenv("DB_FILE")
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

    item_id   = Column(Integer, primary_key=True)
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

def count_my_items(chat_id):
    return len(get_my_items(chat_id))

def get_my_items(chat_id):
    return session.query(Item).filter_by(chat_id=chat_id).order_by(desc(Item.timestamp)).all()

def get_item_by_id(item_id):
    return session.query(Item).filter_by(item_id=item_id).first()
