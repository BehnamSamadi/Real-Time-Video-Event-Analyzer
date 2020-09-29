from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Stream(db.Model):
    __tablename__ = 'stream'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    sample_duration = db.Column(db.Float)
    sample_size = db.Column(db.Integer)
    active_delay = db.Column(db.Float)
    sensitivity = db.Column(db.Float)

class Log(db.Model):
    __tablename__ = 'log'
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'))
    time = db.Column(db.DateTime)
    event_type = db.Column(db.Integer, db.ForeignKey('event.id'))
    confidence = db.Column(db.Float)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class VideoRecord(db.Model):
    __tablename__ = 'videorecord'
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(255))
    label = db.Column(db.Integer, db.ForeignKey('event.id'))

