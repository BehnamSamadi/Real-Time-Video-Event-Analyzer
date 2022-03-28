from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, rooms
from sqlalchemy import desc, func, and_
from models import db, Event, Log, Stream, VideoRecord
from uuid import uuid4
import os
import utils
import datetime
from dateutil import parser
from celery_app import celery_app
from flask_cors import CORS


DEFAULT_FRAME_SIZE = [256, 256]
VIDEO_URL_PREFIX = 'http://192.168.43.78:9000/videos/saved_clips/'

SQLALCHEMY_TRACK_MODIFICATIONS = False
app = Flask("backend_app")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['CELERY_BROKER'] = os.getenv('CELERY_BROKER')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI', "sqlite:///db.sqlite")
db.init_app(app)
db.create_all(app=app)
# socket = SocketIO(app, cors_allowed_origins='*')
ml_status = None

def get_camera_names():
    names = {}
    res = Stream.query.all()
    for r in res:
        names[r.id] = r.name
    return names


@app.route('/update_status', methods=['POST'])
def update_status():
    stream_status = request.json
    stream_id = str(stream_status['stream_id'])
    date = stream_status['datetime']
    date = parser.parse(date)
    confidence = stream_status['confidence']
    clip_id = stream_status['clip_id']
    log = Log(stream_id=stream_id, date=date, confidence=confidence, clip_id=clip_id)
    db.session.add(log)
    db.session.commit()
    print('new status update', log)
    return 'success'


@app.route('/add_stream', methods=['POST'])
def add_stream():
    print(request.json)
    stream_props = utils.parse_stream_prop(request.json)
    print(stream_props)
    if stream_props:
        stream_id = str(uuid4())
        db_stream = Stream(id=stream_id,
                            name=stream_props['name'],
                            url=stream_props['url'],
                            frame_width=DEFAULT_FRAME_SIZE[0],
                            frame_height=DEFAULT_FRAME_SIZE[1],
                            sample_duration=stream_props['sample_duration'],
                            sample_size=stream_props['sample_size'],
                            active_delay=stream_props['active_delay'],
                            sensitivity=stream_props['sensitivity'],
                            long=stream_props['location']['lng'],
                            lat=stream_props['location']['lat'],
                        )
        
        stream_props['id'] = stream_id
        stream_props['frame_size'] = DEFAULT_FRAME_SIZE
        celery_app.send_task('decoder.add_stream', (stream_props,))
        db.session.add(db_stream)
        db.session.commit()
        res = jsonify({
            'status': 'success'})
        return res
    return jsonify({
            'status': 'success'})


@app.route('/remove_stream/<id>', methods=['DELETE'])
def remove_stream(id):
    if id is not None:
        removal = Stream.query.get(id)
        if removal:
            db.session.delete(removal)
            db.session.commit()
            celery_app.send_task('decoder.remove_stream', (str(id),))
            return {
                'status': 'success'
            }
    return {
        'status': 'failed'
        }

@app.route('/logs', methods=['GET'])
def get_logs():
    camera_names = get_camera_names()
    pre_logs = Log.query.filter(Log.confidence>-1).order_by(desc(Log.date))
    logs = []
    for pl in pre_logs:
        print(pl)
        log = {
            'cameraId': pl.stream_id,
            'cameraName': camera_names[pl.stream_id],
            'videoUrl': VIDEO_URL_PREFIX + str(pl.clip_id) + '.mp4',
            'status': 'ANOMALY',
            'date': pl.date,
            'showVideo': False
        }
        logs.append(log)
    return jsonify(logs)


@app.route('/streams', methods=['GET'])
def fetch_streams():
    res = Stream.query.all()
    print(res)
    res_json = [r.get_json() for r in res]
    return jsonify(res_json)


@app.route('/streams/status', methods=['GET'])
def fetch_status():
    subq = db.session.query(
        Log.stream_id,
        func.max(Log.date).label('maxdate')
    ).group_by(Log.stream_id).subquery('t2')

    query = db.session.query(Log).join(
        subq,
        and_(
            Log.stream_id == subq.c.stream_id,
            Log.date == subq.c.maxdate
        )
    )
    status = []
    for l in query.all():
        s = {'id': l.stream_id}
        if l.confidence > 0.49:
            s['status'] = 'WARN'
        else:
            s['status'] = 'NORMAL'
        status.append(s)
    return jsonify(status)


@app.route('/stream/<id>', methods=['GET'])
def get_stream_with_id(id):
    stream = Stream.query.get(id)
    if stream:
        stream_props = stream.get_json()
        status_map = []
        logs = Log.query.filter(Log.stream_id==id).order_by(desc(Log.date)).limit(8).all()
        for l in logs:
            status_map.append(l.confidence)
        status_map.reverse()
        if status_map[-1] > 0.49:
            stream_props['status'] = 'WARN'
        else:
            stream_props['status'] = 'NORMAL'
        stream_props['status_map'] = status_map
        return jsonify(stream_props)
    return jsonify({'message': 'Stream not found'})


@app.route('/update_ml', methods=['GET'])
def update_ml():
    global ml_status
    if ml_status in ['PENDING', 'STARTED']:
        stat = {'status': 'RUNNING'}
        return jsonify(stat)
    ml_status = celery_app.send_task('core.update_ml')
    stat = {
        'task_id': ml_status.task_id,
        'status': 'STARTED'
    }
    return jsonify(stat)

@app.route('/get_ml_status/<task_id>')
def get_ml_status(task_id):
    # res = celery_app.AsyncResult(task_id)
    res = {'status': 'DONE'}
    return jsonify(res.status())


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)
    # socket.run(app, '0.0.0.0', port=5000)
