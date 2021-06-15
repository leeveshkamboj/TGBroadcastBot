from sqlalchemy import Column, BigInteger
from sqlhelper import SESSION, BASE


class channels(BASE):
    __tablename__ = "channels"
    chat_id = Column(BigInteger, primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


channels.__table__.create(checkfirst=True)


def in_channels(chat_id):
    try:
        if SESSION.query(channels).filter(channels.chat_id == chat_id).one():
            return True
        else:
            return False
    except:
        return False
    finally:
        SESSION.close()


def add_channel(chat_id):
    adder = channels(chat_id)
    SESSION.add(adder)
    SESSION.commit()


def rm_channel(chat_id):
    rem = SESSION.query(channels).get(chat_id)
    if rem:
        SESSION.delete(rem)
        SESSION.commit()


def get_all_channels():
    rem = SESSION.query(channels).all()
    SESSION.close()
    return rem