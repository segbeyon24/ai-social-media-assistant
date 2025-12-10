import os
import redis
import rq
from time import sleep
import httpx


REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis_conn = redis.from_url(REDIS_URL)
queue = rq.Queue('default', connection=redis_conn)


# Worker job: publish to a social platform (placeholder)
def publish_post(scheduled_post_id: str, content: str, social_account: dict):
print('Publishing', scheduled_post_id)
sleep(1)
# TODO: call platform API using social_account tokens
return {'status': 'sent', 'post_id': f'post_{scheduled_post_id}'}


if __name__ == '__main__':
# Not run as script in the container; worker_start.sh runs rq worker command
pass