from celery.schedules import crontab

CELERY_TASK_SERIALIZER = 'json'
CELERY_IMPORTS = ('tasks')
CELERY_IGNORE_RESULT = False
BROKER_URL = 'redis://'
CELERY_RESULT_BACKEND = 'redis://'

CELERYBEAT_SCHEDULE = {
    'every-minute': {
        'task': 'tasks.say_hello',
        'schedule': crontab(minute='*/1'),
    },
}
