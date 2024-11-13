import os
from dotenv import load_dotenv
from flask import Flask
from adapters.api.routes import register_routes
from extensions import db, cors, jwt
from flask_restful import Api


# Determinar el entorno
environment = os.getenv('FLASK_ENV', 'production')  # Por defecto 'local'
if environment == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.local')

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("SERVER_DATABASE")}/{os.getenv("DB_NAME")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    app.config['NFS_DIRECTORY'] = os.environ.get('NFS_DIRECTORY')
    app.config['LOGO_PATH']= os.environ.get('LOGO_PATH')
    app.config['VIDEO_LOGO']= os.environ.get('VIDEO_LOGO')
    app.config['ALLOWED_EXTENSIONS'] = os.environ.get('ALLOWED_EXTENSIONS')
    app.config['PROCESSED_DIR'] = os.environ.get('PROCESSED_DIR')
    app.config['JWT_SECRET_KEY'] = 'secret'
    app.config['PROPAGATE_EXCEPT'] = os.environ.get('PROPAGATE_EXCEPT')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')
    app.config['broker_url'] = os.getenv('CELERY_BROKER_URL', os.environ.get('CELERY_BROKER_URL'))
    app.config['result_backend'] = os.getenv('CELERY_RESULT_BACKEND', os.environ.get('CELERY_RESULT_BACKEND'))
    
    app.config['broker_connection_retry_on_startup'] = True

    db.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()
        
    api = Api(app)
    register_routes(api)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
