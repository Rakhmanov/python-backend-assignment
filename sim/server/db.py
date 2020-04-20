import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.sql import func

from sqlalchemy import (
    Binary,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

class Base(object):
    @declared_attr
    def as_dict(self):
        raise NotImplementedError()

    @classmethod 
    def uuid4_s(cls):
        return str(uuid.uuid4())

Base = declarative_base(cls=Base)


"""
Column definitions could be further optimized to include length of the intended values, and indexes.
"""
class Animal(Base):
    __tablename__ = 'animals'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    species = Column(String)
    author_id = Column(Integer, ForeignKey('users.id'))

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
        }

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    last_name = Column(String)
    email = Column(String, index=True, unique=True)
    password = Column(String)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email
        }

class AccessLog(Base):
    """AccessLog

    This table is useful to track usage and bill.
    Far from HIPPA Detail level though.
    """
    __tablename__ = 'access_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    client_ip = Column(String)
    resource = Column(String)
    method = Column(String)
    body = Column(Binary)
    timestamp = Column(DateTime, server_default=func.datetime('now'))

    def as_dict(self):
        return {
            'id': self.id,
            'user': self.user.name,
            'client_ip': self.client_ip,
            'resource': self.resource,
            'method': self.method,
            'timestamp': self.timestamp,
        }


class Session(Base):
    """ Session
    
    Length is set on the database server, ideally it would be a setting in the application.
    With ability to revoke and expire sesison.
    """
    __tablename__ = 'sessions'

    id = Column(String, default=Base.uuid4_s, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    client_ip = Column(String)
    timestamp = Column(DateTime, server_default=func.datetime('now'))
    expiry = Column(DateTime, server_default=func.datetime('now', '30 minutes'))

    def is_expired(self):
        return datetime.utcnow() > self.expiry

    def as_dict(self):
        return {
            'id': self.id,
            'user': self.name,
            'timestamp': self.timestamp,
            'expired': self.is_expired(),
        }
 
User.animals = relationship('Animal')
User.sessions = relationship('Session', cascade="all, delete, delete-orphan", order_by=Session.timestamp, backref='user')
User.access_logs = relationship('AccessLog', order_by=AccessLog.id, backref='user', lazy='noload')

class Database(object):
    def __init__(self, config):
        self.config = config
        connection_string = 'sqlite:///{0}'.format(self.config['db'])
        self._engine = create_engine(connection_string, echo=True)
        self._sessionmaker = sessionmaker(bind=self._engine)
        Base.metadata.create_all(self._engine)

    def create_session(self):
        return self._sessionmaker()
