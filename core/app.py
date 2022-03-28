"""
This script runs a pipeline for classification and training
"""
from celery_app import app
from result_manager import ResultManager
from train import ModelTrainer
from classifier import Classifier
import os


vector_db_path = os.getenv('VECTOR_DB_PATH')
queue_name = os.getenv('INPUT_DATA_QUEUE_NAME', 'queue:clips')
classifier_min_distance = float(os.getenv('MIN_KNN_DISTANCE', 0.3))
video_dataset_path = os.getenv('DATASET_PATH', './dataset')

clf = Classifier(vector_db_path, min_distance=classifier_min_distance)
res_man = ResultManager(app, clf, queue_name)
trainer = ModelTrainer(app, clf)

@app.task(name='core.run_pipeline')
def run_pipeline():
    res_man.run()


@app.task(name='core.update_ml')
def update_ml():
    print('train request recived')
    trainer.train(video_dataset_path)
    return True

pipe = run_pipeline.delay()






