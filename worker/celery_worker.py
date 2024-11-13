from app import create_app
from worker.celery_config import make_celery

app = create_app()
celery = make_celery(app)

import messagingQueue.tasks
