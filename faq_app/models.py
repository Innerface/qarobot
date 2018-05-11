from faq_app.db_connect import db
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR, TIMESTAMP, INTEGER


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


class Question_auto(db.Model):
    __tablename__ = 'question_auto'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100), unique=True)
    answer = db.Column(db.Text, unique=True)
    agrees = db.Column(db.Integer, unique=True)
    words = db.Column(db.String(32), unique=True)
    platform = db.Column(db.String(5), unique=True)
    simi = db.Column(db.String(32), unique=True)

    def roll_back(self):
        db.session.remove()


class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(INTEGER, primary_key=True)
    client_code = db.Column(VARCHAR(length=32))
    client_name = db.Column(VARCHAR(length=32))
    open_id = db.Column(VARCHAR(length=32))
    ip = db.Column(VARCHAR(length=16))
    phone = db.Column(VARCHAR(length=16))
    platform = db.Column(TINYINT(unsigned=True))
    create_time = db.Column(TIMESTAMP())


class Synonyms(db.Model):
    __tablename__ = 'synonyms'
    id = db.Column(INTEGER, primary_key=True)
    word = db.Column(VARCHAR(length=16))
    parent_id = db.Column(INTEGER)
    count = db.Column(INTEGER)
    status = db.Column(TINYINT(unsigned=True))
    create_time = db.Column(TIMESTAMP())


class Emotional(db.Model):
    __tablename__ = 'emotional'
    id = db.Column(INTEGER, primary_key=True)
    word = db.Column(VARCHAR(length=16))
    type = db.Column(VARCHAR(length=32))
    emotion_type = db.Column(VARCHAR(length=32))
    count = db.Column(INTEGER)
    status = db.Column(TINYINT(unsigned=True))
    create_time = db.Column(TIMESTAMP())


class Sensitive(db.Model):
    __tablename__ = 'sensitive'
    id = db.Column(INTEGER, primary_key=True)
    word = db.Column(VARCHAR(length=16))
    type = db.Column(TINYINT(unsigned=True))
    count = db.Column(INTEGER)
    status = db.Column(TINYINT(unsigned=True))
    create_time = db.Column(TIMESTAMP())
