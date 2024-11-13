import os
from sqlite3 import OperationalError
from flask import jsonify, request, url_for, send_from_directory
from flask_restful import Resource, reqparse
from core.schemas import TaskSchema, UserSchema, VideoSchema
from core.services import TaskService, UserService, VideoService
from flask_jwt_extended import create_access_token

class UserController(Resource):
    def __init__(self):
        self.user_service = UserService()
    
    def post(self):
        if request.path == '/api/auth/signup':
            return self.signup()
        elif request.path == '/api/auth/login':
            return self.login()

    def signup(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('username', required=True, help='Username cannot be blank')
            parser.add_argument('email', required=True, help='Email cannot be blank')
            parser.add_argument('password', required=True, help='Password cannot be blank')
            parser.add_argument('password2', required=True, help='Password2 cannot be blank')
            args = parser.parse_args()

            if args.password != args.password2:
                return {"message": "Las contraseñas no coinciden."}, 400
            user = self.user_service.create_user(args)
            token_acceso=create_access_token(identity=user.id)
            return {
                'user': UserSchema().dump(user),
                'token': token_acceso
            }, 201
        except OperationalError as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500    
    
    def login(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('username', required=True, help='Username cannot be blank')
            parser.add_argument('password', required=True, help='Password cannot be blank')
            parser.add_argument('email', required=True, help='Password cannot be blank')
            args = parser.parse_args()

            user = self.user_service.login(args)

            if user:
                token_de_acceso = create_access_token(identity=user.id)
                return {"mensaje": "Login successful", "token": token_de_acceso}
            else:
                return {'message': 'Invalid username or password'}, 401
        except OperationalError as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500
            
class VideoController(Resource):
    
    def get(self, filename=None):
        if filename is not None:  
            return self.get_file_video(filename)
        else:  
            return self.get_all_videos()

    def get_file_video(self, filename):
        try:
            return send_from_directory(os.environ.get('NFS_DIRECTORY'), filename)
        except OperationalError as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500
            
    def get_all_videos(self):
        try:
            video_service = VideoService()
            max_results = request.args.get('max', type=int)
            order = request.args.get('order', type=int, default=0)

            videos = video_service.get_all_videos(max_results, order)
            return VideoSchema(many=True).dump(videos), 200
        except OperationalError as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500

class TaskController(Resource):
        
    def get(self, id_task=None):
        if id_task is not None:  
            return self.get_task_by_id(id_task)
        else:  
            return self.get_all_tasks()
        
    def get_all_tasks(self):
        try:
            task_service = TaskService()
            max_results = request.args.get('max', type=int)
            order = request.args.get('order', type=int, default=0)

            tasks = task_service.get_all_tasks(max_results, order)
            return TaskSchema(many=True).dump(tasks), 200
        except OperationalError as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500


    def get_task_by_id(self, id_task):
        try:
            task_service = TaskService()
            result = task_service.get_task_by_id(id_task)
            if result:
                return {
                    'task': TaskSchema().dump(result['task']),
                    'video_url': result['video_url']
                }, 200
            else:
                return {"msg": "Task not found"}, 404
        except OperationalError as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500
        
    def post(self):
        try:
            task_service = TaskService()
            file = request.files.get('file')
            if file is None or file.filename == '':
                return {'message': 'No selected file'}, 400

            allowed= file.filename.rsplit('.', 1)[1].lower() in os.environ.get('ALLOWED_EXTENSIONS', '').split(',')            
            if not allowed: 
                return {'message': 'File type not allowed'}, 400
            
            file_path = os.path.join(os.environ.get('UPLOAD_FOLDER'), file.filename)
            if os.path.exists(file_path):
                return {"message": "The file already exists."}, 409 

            task = TaskSchema().dump(task_service.create_task(file))

            return {
                "task": "Task created successfully",
                "id": task['id'],  
                "timestamp": task['timestamp'], 
                "status": task['status'],  
                "filename": task['filename']  
            }, 201
        except OperationalError as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500


    def delete(self, id_task):
        try:
            task_service = TaskService()
            if task_service.delete_task(id_task):
                return jsonify({"message": "Task deleted successfully"})
            return jsonify({"message": "Task not found"}), 404
        except OperationalError as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "There was an issue accessing the database.",
                    "details": error_message  
                }
            }, 500
        except Exception as e:
            error_message = str(e)  
            return {
                "error": {
                    "message": "An unexpected error occurred.",
                    "details": error_message  
                }
            }, 500
    
   
    
        