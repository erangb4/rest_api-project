from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
from project.Logger import Logger


config = ConfigParser()
config.read("config.conf")
connection_string = config["db"]["conn_string"]

logger = Logger.get_instance()

Base = declarative_base()

Session = sessionmaker()
engine = create_engine(connection_string, echo=True)
local_session = Session(bind=engine)


def create_all_entities():
    try:
        Base.metadata.create_all(engine)
        logger.logger.debug('all the sql tables created.')
    except OperationalError:
        print('The database did not found, please check the connection string')
        logger.logger.critical('The database did not found, please check the connection string')
