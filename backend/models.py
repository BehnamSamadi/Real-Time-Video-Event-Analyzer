from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Stream(db.Model):
    __tablename__ = 'stream'
    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    frame_height = db.Column(db.Integer)
    frame_width = db.Column(db.Integer)
    sample_duration = db.Column(db.Float)
    sample_size = db.Column(db.Integer)
    active_delay = db.Column(db.Float)
    sensitivity = db.Column(db.Float)
    long = db.Column(db.Float)
    lat = db.Column(db.Float)

    def get_json(self):
        res = {
            'id': self.id,
            'url': self.url,
            'name': self.name,
            'frame_size': [self.frame_width, self.frame_height],
            'sample_duration': self.sample_duration,
            'sample_size': self.sample_size,
            'active_delay': self.active_delay,
            'sensitivity': self.sensitivity,
            'location': [self.lat, self.long]
        }
        return res


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.String(255), db.ForeignKey('stream.id'))
    date = db.Column(db.DateTime)
    # event_type = db.Column(db.Integer, db.ForeignKey('event.id'))
    confidence = db.Column(db.Float)
    clip_id = db.Column(db.String(255))

    def get_json(self):
        res = {
            'stream_id': self.stream_id,
            'date': self.date,
            'confidence': self.confidence,
            'clip_id': self.clip_id
        }
        return res
    
    def __str__(self) -> str:
        return "id: {} stream-id:{} date:{} confidence:{:.3f} clip_id:{}".format(self.id,
                             self.stream_id, self.date, self.confidence, self.clip_id)

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
