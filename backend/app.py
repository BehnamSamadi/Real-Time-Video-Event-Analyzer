from flask import Flask, request, jsonify
from models import db, Event, Log, Stream, VideoRecord
from celery import Celery
import os
import utils


app = Flask("backend_app")
app.config['CELERY_BROKER'] = os.getenv('CELERY_BROKER')
db.init_app(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


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
        
        celery.send_task('decoder.add_stream', stream_props)
        db.session.add(db_stream)
        dv.session.commit()
        return {
            'status': 'success'
        }
    return {
        'status': 'failed'
        }

@app.route('/remove_stream', methods=['POST'])
def remove_stream():
    stream_id = utils.parse_stream_id(request)
    if stream_id:
        removal = Stream.query.fillter_by(id=stream_id).first()
        if removal:
            db.session.delete(removal)
            db.session.commit()
            celery.send_task('decoder.remove_stream', stream_id)
            return {
                'status': 'success'
            }
    return {
        'status': 'failed'
        }


@app.route('/fetch_streams', methods=['GET'])
def fetch_streams():
    res = Stream.query.all()
    return res
