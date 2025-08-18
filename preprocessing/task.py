# preprocessing/tasks.py
import time
from celery import shared_task
from django.utils import timezone
from .models import PreprocessingJob
import pandas as pd
import io

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_preprocessing_job(self, job_id):
    job = PreprocessingJob.objects.get(pk=job_id)
    job.status = PreprocessingJob.Status.RUNNING
    job.started_at = timezone.now()
    job.save(update_fields=['status', 'started_at'])

    try:
        df = pd.read_csv(job.dataset.file.path)
        df_clean = df.dropna()
        buffer = io.StringIO()
        df_clean.to_csv(buffer, index=False)
        buffer.seek(0)

        job.result_file.save(
            f'pre_{job.dataset.file.name}',
            io.BytesIO(buffer.read().encode()),
            save=False
        )

        job.status = PreprocessingJob.Status.SUCCESS
        job.finished_at = timezone.now()
        job.log += f"\n Procesadas {len(df_clean)} filas."
        job.save()
    except Exception as exc:
        job.status = PreprocessingJob.Status.FAILED
        job.finished_at = timezone.now()
        job.error_message = str(exc)
        job.log += f"\n ERROR: {exc}"
        job.save()
        raise self.retry(exc=exc)


