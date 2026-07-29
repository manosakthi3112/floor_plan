import json
import uuid
from datetime import datetime

from app.config import settings


class JobQueue:
    def __init__(self):
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            import redis.asyncio as aioredis
            self._redis = await aioredis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    async def enqueue(self, job_type: str, payload: dict) -> str:
        r = await self._get_redis()
        job_id = str(uuid.uuid4())
        job = {
            'id': job_id,
            'type': job_type,
            'status': 'queued',
            'progress': 0.0,
            'payload': json.dumps(payload),
            'created_at': datetime.utcnow().isoformat(),
        }
        await r.rpush(f'queue:{job_type}', json.dumps(job))
        await r.hset(f'job:{job_id}', mapping=job)
        return job_id

    async def get_job(self, job_id: str) -> dict | None:
        r = await self._get_redis()
        data = await r.hgetall(f'job:{job_id}')
        if not data:
            return None
        return {k: json.loads(v) if k in ('payload',) else v for k, v in data.items()}

    async def update_job(self, job_id: str, **updates):
        r = await self._get_redis()
        await r.hset(f'job:{job_id}', mapping=updates)

    async def subscribe(self, job_id: str):
        r = await self._get_redis()
        pubsub = r.pubsub()
        await pubsub.subscribe(f'job:progress:{job_id}')
        return pubsub

    async def publish_progress(self, job_id: str, progress: float, status: str, result: dict | None = None):
        r = await self._get_redis()
        msg = {'job_id': job_id, 'progress': progress, 'status': status}
        if result:
            msg['result'] = result
        await r.publish(f'job:progress:{job_id}', json.dumps(msg))
        await self.update_job(job_id, progress=str(progress), status=status)


job_queue = JobQueue()
