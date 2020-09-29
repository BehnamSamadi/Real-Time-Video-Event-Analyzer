from flask import Flask, request, jsonify
from models import Event, Log, Stream, VideoRecord

app = Flask("backend_app")




@app.route('/add_stream', methods=['POST'])
def add_stream():
    pass


@app.route('/remove_stream', methods=['POST'])
def remove_stream():
    pass

