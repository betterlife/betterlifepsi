from sqlalchemy import Column, Integer, String
from database import Base


class Entry(Base):
    __tablename__ = 'entry'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=False)
    text = Column(String(4096), unique=False)

    # def __init__(self, title, text):
    #    self.title = title
    #    self.text = text

    def __repr__(self):
        return '<Entry %r>' % self.title
