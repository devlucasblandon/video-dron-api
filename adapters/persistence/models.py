from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enums.enums import TaskStatus
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    videos = relationship('Video', back_populates='user')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Video(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, nullable=False)
    size = db.Column(db.String, nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    processed_path = db.Column(db.String, nullable=True)  # Ruta del video procesado
    
    user = relationship('User', back_populates='videos')
    tasks = relationship('Task', back_populates='video')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    video_id = db.Column(db.Integer, ForeignKey('video.id'), nullable=False)
    
    video = relationship('Video', back_populates='tasks')
    
