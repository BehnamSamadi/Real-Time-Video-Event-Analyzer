"""
This script runs a pipeline for classification and training
"""
from celery_app import app
from result_manager import ResultManager
import os


vector_db_path = os.getenv('VECTOR_DB_PATH')
queue_name = os.getenv('INPUT_DATA_QUEUE_NAME', 'queue:clips')
min_distance = float(os.getenv('MIN_KNN_DISTANCE', 0.6))
video_dataset_path = os.getenv('DATASET_PATH', './dataset')

res_man = ResultManager(app, vector_db_path, queue_name, min_distance)

@app.task(name='core.run_pipeline')
def run_pipeline():
    res_man.run()


@app.task(name='core.update_ml')
def update_ml():
    res_man.update(video_dataset_path)
    return True

pipe = run_pipeline.delay()






