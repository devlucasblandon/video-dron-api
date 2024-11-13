import os
from sqlite3 import OperationalError
from adapters.persistence.models import Task, User, Video
from core.schemas import VideoSchema, TaskSchema
from extensions import db
from enums.enums import TaskStatus
from flask import url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.schemas import VideoSchema
from google.cloud import storage


video_schema=VideoSchema()

class UserService:
    def create_user(self, data):
        new_user = User(username=data['username'], password=data['password'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def login(self, data):
        user = User.query.filter_by(username=data['username'], password=data['password'], email=data['email']).first()
        return user

class TaskService:
    
    def upload_video(self, bucket_name, source_file_name, destination_blob_name):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"Archivo {source_file_name} subido a {destination_blob_name}.")
        
    @jwt_required()
    def create_task(self, file):
        try:
            current_user_id = get_jwt_identity() 
            video = Video(filename=file.filename, size=file.content_length, user_id=current_user_id)
            db.session.add(video)
            db.session.commit()
                
            task = Task(status=TaskStatus.PENDING, filename=file.filename,  video_id=video.id)
            db.session.add(task)
            db.session.commit()
            
            upload_folder = os.environ.get('NFS_DIRECTORY')
            
            print('path',upload_folder)
            
            if not upload_folder or not os.path.exists(upload_folder):
                print("El directorio no existe o no está montado.")
            else:

                if not os.access(upload_folder, os.W_OK):
                    print("No tienes permisos de escritura en el directorio.")
                else:
                    file_path = os.path.join(upload_folder, file.filename)
                    file.save(file_path)
                    print(f"Archivo guardado en: {file_path}")
                    
            bucket_name = os.environ.get('GOOGLE_BUCKET')
            source_file_name = file_path
            destination_blob_name = file.filename

            self.upload_video(bucket_name, source_file_name, destination_blob_name)
            
            from messagingQueue.tasks import process_video
            process_video.apply_async(args=[VideoSchema().dump(video), TaskSchema().dump(task)])
            return task
        except OperationalError as e:
            db.session.rollback()
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            db.session.rollback()
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500
            
            
    @jwt_required()
    def get_all_tasks(self, max_results=None, order=0):
        current_user_id = get_jwt_identity()
        
        query = Task.query.join(Video).filter(
        Video.user_id == current_user_id,
        Task.status == TaskStatus.PROCESSED )

        if order == 1:
            query = query.order_by(Task.id.desc())
        else:
            query = query.order_by(Task.id.asc())

        if max_results:
            query = query.limit(max_results)

        return query.all()

    @jwt_required()
    def get_task_by_id(self, id_task):
        current_user_id = get_jwt_identity()
        task = Task.query.join(Video).filter(
            Task.id == id_task,
            Video.user_id == current_user_id
        ).first()
        if task:
            video_url = url_for('get_video', filename=os.environ.get('PREFIX_FILE')+(task.filename), _external=True)
            return {
                'task': task,
                'video_url': video_url
            }
        return None
    
    
    @jwt_required()
    def delete_task(self, id_task):
        task = Task.query.join(Video).filter(
            Task.id == id_task
        ).first()
        
        if task and task.status == TaskStatus.PROCESSED:
            processed_file_path = os.path.join(os.environ.get('PROCESSED_DIR'), os.environ.get('PREFIX_FILE')+task.filename)
            original_file_path = os.path.join(os.environ.get('UPLOAD_FOLDER'), task.filename)
            if os.path.exists(processed_file_path):
                os.remove(processed_file_path)
            else:
                print("File  processed not exists:", processed_file_path)
            if os.path.exists(original_file_path):
                os.remove(original_file_path)
            else:
                print("File original not exists:", original_file_path)
                
            db.session.delete(task.video)    
            db.session.delete(task)
            db.session.commit()
            return True
        return False

class VideoService:
    
    def get_all_videos(self, max_results=None, order=0):
        query = Video.query

        if order == 1:
            query = query.order_by(Video.id.desc())
        else:
            query = query.order_by(Video.id.asc())

        if max_results:
            query = query.limit(max_results)
        videos = query.all()
        result = []
        for video in videos:   
            video_url = url_for('get_video', filename=os.environ.get('PREFIX_FILE') + video.filename, _external=True)
            result.append({
                'id': video.id,  
                'filename': video.filename,  
                'size': video.size,
                'created_at': video.created_at,
                'video_url': video_url
            })
        
        return result