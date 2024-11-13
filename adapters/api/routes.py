from flask_restful import Api
from adapters.api.controllers import UserController,TaskController,VideoController


def register_routes(api:Api):
    api.add_resource(UserController, '/api/auth/signup', endpoint='user_signup')
    api.add_resource(UserController, '/api/auth/login', endpoint='user_login')
    api.add_resource(TaskController, '/api/tasks/<int:id_task>', endpoint='task_list_by_id')
    api.add_resource(VideoController, '/api/videos', endpoint='video_list')
    api.add_resource(TaskController, '/api/tasks', endpoint='task_create')
    api.add_resource(TaskController, '/api/tasks', endpoint='task_list')
    api.add_resource(TaskController, '/api/tasks/<int:id_task>',endpoint='task_delete__by_id')
    api.add_resource(VideoController,'/downloads/<path:filename>', endpoint='get_video')
