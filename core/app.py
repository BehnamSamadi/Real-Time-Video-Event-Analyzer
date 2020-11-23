"""
This script runs a pipeline for classification and training
"""
import celery
from result_manager import ResultManager
import os


broker = os.getenv('SP_BROKER_URL', 'amqp://localhost:5672/')
vector_db_path = os.getenv('VECTOR_DB_PATH')
queue_name = os.getenv('INPUT_DATA_QUEUE_NAME', 'queue:data')
min_distance = float(os.getenv('MIN_KNN_DISTANCE', 0.6))
video_db = os.getenv('DATASET_PATH', './dataset')


app = celery.Celery()
res_man = ResultManager(vector_db_path, queue_name, min_distance)

@app.task
def run_pipeline():
    res_man.run()


@app.task(name='update_ml')
def update_ml():
    res_man.update(video_db)

pipe = run_pipeline.delay()







