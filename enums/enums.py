import enum

class TaskStatus(enum.Enum):
    UPLOADED = 'uploaded'
    PROCESSED = 'processed'
    PENDING = 'pending'
    FAILURE = 'failure'
    PROCESSING = "PROCESSING"