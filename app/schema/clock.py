import time
from datetime import datetime

from rx import Observable

from .base import schema


@schema.subscription.field('current_time')
def subscribe_current_time(root, info) -> str:
    return Observable.from_iterable(poll_current_time())


def poll_current_time():
    while True:
        yield datetime.utcnow().strftime('%H:%M:%S')
        time.sleep(1)
