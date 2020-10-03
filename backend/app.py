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
        celery.send_task('decoder.add_stream', stream_props)
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
        celery.send_task('decoder.remove_stream', stream_id)
        return {
            'status': 'success'
        }
    return {
        'status': 'failed'
        }



@app.route('/fetch_streams', methods=['GET'])
def fetch_streams():
    
    pass


