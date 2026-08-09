import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()


def make_celery():
    from app import create_app

    flask_app = create_app()

    celery = Celery(
        flask_app.import_name,
        broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    )

    celery.conf.update(
        result_serializer="json",
        accept_content=["json"],
        task_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )

    celery.conf.beat_schedule = {
        "send-daily-reminders": {
            "task": "app.tasks.reminders.send_daily_reminders",
            "schedule": crontab(hour=8, minute=0),  # Every day at 08:00 UTC
        },
        "generate-monthly-report": {
            "task": "app.tasks.reports.generate_monthly_report",
            "schedule": crontab(day_of_month=1, hour=6, minute=0),  # 1st of month, 06:00 UTC
        },
    }

    celery.autodiscover_tasks(["app.tasks"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = make_celery()
