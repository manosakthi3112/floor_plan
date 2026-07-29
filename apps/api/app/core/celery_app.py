"""
Celery configuration for async task processing.

Install: pip install celery[redis]
Run worker: celery -A app.core.celery_app worker --loglevel=info

Usage:
    from app.core.celery_app import celery_app

    @celery_app.task
    def process_parsing_job(job_id: str):
        ...
"""

# from celery import Celery
# from app.config import settings
#
# celery_app = Celery(
#     'plancraft3d',
#     broker=settings.redis_url,
#     backend=settings.redis_url,
# )
#
# celery_app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json',
#     timezone='UTC',
#     enable_utc=True,
#     task_track_started=True,
#     task_acks_late=True,
#     worker_prefetch_multiplier=1,
# )
