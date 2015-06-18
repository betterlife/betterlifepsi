from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# import all modules here that might define models so that
# they will be registered properly on the metadata.  Otherwise
# you will have to import them first before calling init_db()
import os

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_database():
    from models import Product, ProductCategory, Supplier
    Base.metadata.create_all(bind=engine)
    return db_session
