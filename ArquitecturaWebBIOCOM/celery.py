import os, time
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ArquitecturaWebBIOCOM.settings")
os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")

app = Celery("ArquitecturaWebBIOCOM")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

