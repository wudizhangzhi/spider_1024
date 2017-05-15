# -*- coding:utf8 -*-
BROKER_URL = 'redis://localhost:6379//1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379//1'
from celery.schedules import crontab


CELERYBEAT_SCHEDULE = {
    'update-video-data:12:00': {
        'task': 'core.tasks.auto_general_deposit',
        'schedule': crontab(hour=12)
    },
}
