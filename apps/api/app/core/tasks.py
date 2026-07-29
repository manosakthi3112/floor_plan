"""Celery tasks for async job processing.

Uncomment when Celery worker is running.
"""

# from app.core.celery_app import celery_app
# from app.core.job_queue import job_queue
#
#
# @celery_app.task(bind=True, max_retries=3)
# def process_parsing(self, job_id: str, image_url: str):
#     import httpx
#     from app.orchestrator import parse_floor_plan
#
#     job_queue.update_job(job_id, status='processing', progress=0.1)
#
#     try:
#         resp = httpx.get(image_url)
#         graph = parse_floor_plan(resp.content)
#
#         job_queue.update_job(job_id, status='done', progress=1.0)
#         return graph.model_dump()
#     except Exception as exc:
#         job_queue.update_job(job_id, status='error', error_message=str(exc))
#         raise self.retry(exc=exc)
