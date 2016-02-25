from server import celery


@celery.task()
def say_hello():
    print "HERE"
