from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    Column,
    Integer,
    String,
)


Base = declarative_base()


class Animal(Base):
    __tablename__ = 'animals'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    species = Column(String)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
        }


class Database(object):
    def __init__(self, config):
        self.config = config
        connection_string = 'sqlite:///{0}'.format(self.config['db'])
        self._engine = create_engine(connection_string)
        self._sessionmaker = sessionmaker(bind=self._engine)

    def create_session(self):
        return self._sessionmaker()
