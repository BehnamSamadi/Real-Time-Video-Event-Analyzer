from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, rooms
from models import db, Event, Log, Stream, VideoRecord
import os
import utils
import datetime
from celery_app import celery_app


app = Flask("backend_app")
app.config['CELERY_BROKER'] = os.getenv('CELERY_BROKER')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URI', "sqlite:///db.sqlite")
db.init_app(app)
db.create_all()
socket = SocketIO(app, cors_allowed_origins='*')
ml_status = None


@app.route('/update_status', methods=['POST'])
def update_status():
    stream_status = request.json
    stream_id = stream_status['stream_id']
    time = stream_status['datetime']
    time = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
    confidence = stream_status['confidence']
    socket.emit('log', stream_status, broadcast=True)
    log = Log(stream_id=stream_id, time=time, confidence=confidence)
    db.session.add(log)
    db.session.commit()


@app.route('/add_stream', methods=['POST'])
def add_stream():
    stream_props = utils.parse_stream_prop(request)
    if stream_props:
        db_stream = Stream(id=stream_props['id'],
                            address=stream_props['address'],
                            sample_duration=stream_props['sample_duration'],
                            sample_size=stream_props['sample_size'],
                            active_delay=stream_props['active_delay'],
                            sensitivity=stream_props['sensitivity']
                        )
        
        celery.send_task('decoder.add_stream', (stream_props,))
        db.session.add(db_stream)
        db.session.commit()
        return {
            'status': 'success'
        }
    return {
        'status': 'failed'
        }


@app.route('/remove_stream', methods=['POST'])
def remove_stream():
    req = request.json
    stream_id = utils.parse_stream_id(req)
    if stream_id:
        removal = Stream.query.fillter_by(id=stream_id).first()
        if removal:
            db.session.delete(removal)
            db.session.commit()
            celery_app.send_task('decoder.remove_stream', (stream_id,))
            return {
                'status': 'success'
            }
    return {
        'status': 'failed'
        }


@app.route('/fetch_streams', methods=['GET'])
def fetch_streams():
    res = Stream.query.all()
    res_json = [r.get_json() for r in res]
    return jsonify(res_json)

@app.route('/update_ml', methods=['GET'])
def update_ml():
    global ml_status
    if ml_status and ml_status.status in ['PENDING', 'STARTED']:
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
    res = celery_app.AsyncResult(task_id)
    return jsonify(res.status())


if __name__ == "__main__":
    socket.run(app, '0.0.0.0', port=5000)
