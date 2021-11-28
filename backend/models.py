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

    def get_json(self):
        res = {
            'id': self.id,
            'address': self.address,
            'sample_duration': self.sample_duration,
            'sample_size': self.sample_size,
            'active_delay': self.active_delay,
            'sensitivity': self.sensitivity
        }
        return res


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'))
    time = db.Column(db.DateTime)
    # event_type = db.Column(db.Integer, db.ForeignKey('event.id'))
    confidence = db.Column(db.Float)

    def get_json(self):
        res = {
            'stream_id': self.stream_id,
            'time': self.time,
            'confidence': self.confidence
        }
        return res
    
    def __str__(self) -> str:
        return "id: {} stream-id:{} time:{} confidence:{:.3f}".format(self.id, self.stream_id, self.time, self.confidence)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class VideoRecord(db.Model):
    __tablename__ = 'videorecord'
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(255))
    label = db.Column(db.Integer, db.ForeignKey('event.id'))
    
    def get_json(self):
        res = {
            'id': self.id,
            'uri': self.uri,
            'label': self.label
        }
        return res
