# -*- coding:utf8 -*-
from pipelines import SaveItemPipeline
from celery import Celery
from celeryconfig import *

app = Celery('tasks', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND))
app.config_from_object('celeryconfig')



@app.task
def update_video_data():
    # 更新任务队列

@app.task
def update_uper_data():
    pass


@app.task
def update_tag_data():
    pass
