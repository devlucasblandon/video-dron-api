from worker.celery_worker import celery
from app import create_app
from extensions import db
from adapters.persistence.models import Task, User, Video
from enums.enums import TaskStatus
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import resize
from moviepy.editor import *
import os, time, shutil, logging
import subprocess
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError

# Configuracion del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s/%(asctime)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def resize_video(trimmed_clip):
    # Ajustar la relación de aspecto a 16:9
    target_aspect_ratio = 16 / 9
    current_aspect_ratio = trimmed_clip.w / trimmed_clip.h

    if current_aspect_ratio > target_aspect_ratio:
        # Demasiado ancho, recortar los lados
        new_width = int(trimmed_clip.h * target_aspect_ratio)
        x1 = (trimmed_clip.w - new_width) // 2
        x2 = x1 + new_width
        resized_clip = trimmed_clip.crop(x1=x1, x2=x2)
    else:
        # Demasiado alto o en el aspecto correcto, recortar la parte superior/inferior
        new_height = int(trimmed_clip.w / target_aspect_ratio)
        y1 = (trimmed_clip.h - new_height) // 2
        y2 = y1 + new_height
        resized_clip = trimmed_clip.crop(y1=y1, y2=y2)
    return resized_clip  
                
@celery.task(bind=True)
def process_video(self, *args, **kwargs):
    try:
        video_id=args[0]['id']
        task_id=args[1]['id']
        
        logger.info(f"Starting processing of video ID: {video_id}, Task ID: {task_id}")
        
        # Obtener la instancia del video
        video = Video.query.get(video_id)
        if not video:
            raise ValueError(f"No se encontró el video con ID {video_id}")
        logger.info(f"Video encontrado: {video.filename}")
        
        # Obtener la tarea asociada
        task_record = Task.query.get(task_id)
        if not task_record:
            raise ValueError(f"No se encontró la tarea con ID {task_id}")
        logger.info(f"Tarea encontrada: {task_record.id}, Estado: {task_record.status}")
        
        # Actualizar el estado de la tarea a 'PROCESSING'
        task_record.status = TaskStatus.PROCESSING
        db.session.commit()
        logger.info("Estado de la tarea actualizado a PROCESSING")
        
        bucket_name = os.environ.get('GOOGLE_BUCKET')
        destination_path = f"/tmp/{video.filename}" 
        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(video.filename)
            blob.download_to_filename(destination_path)
            logger.info(f"Video descargado desde el bucket a {destination_path}")
        except Exception as e:
            logger.error(f"Error al descargar el video desde el bucket: {e}")
            raise
        
        # Ruta del archivo original
        
        #logger.info("variable de entorno",celery.conf['NFS_DIRECTORY'])
        #original_path = os.path.join(celery.conf['NFS_DIRECTORY'], video.filename)
        
        #logger.info("Se encontro la ruta del archivo original", original_path)
        
        #if not os.path.exists(original_path):
        #    raise FileNotFoundError(f"El archivo original no existe: {original_path}")
        
        # Simular el procesamiento del video
        print(f"Procesando el video: {destination_path}")
        time.sleep(10)
        
        # Procesar el video (ejemplo: copiar el archivo a NFS_DIRECTORY)
        processed_folder = os.environ.get('NFS_DIRECTORY')
        
        if not os.path.exists(processed_folder):
            os.makedirs(processed_folder)
        processed_filename = f"processed_{video.filename}"
        processed_path = os.path.join(processed_folder, processed_filename)

        logger.info(f"Recortando el video y guardando en {processed_path}")
        
        logo_path = os.path.join(celery.conf['LOGO_PATH'], celery.conf['VIDEO_LOGO'])
        
        logo_clip = VideoFileClip(logo_path)
           
        #Recortar el video a 20 segundos y ajustar la relación de aspecto
        with VideoFileClip(destination_path) as video_clip:
            # Recortar a 20 segundos max
            start_time = 0
            end_time = min(15, video_clip.duration)
            trimmed_clip = video_clip.subclip(start_time, end_time)
            resized_clip=resize_video(trimmed_clip)
            
            resized_log_clip=resize_video(logo_clip)
         
            # Concatenar el logo y el video recortado
            final_clip = concatenate_videoclips([resized_log_clip, resized_clip], method="compose")

            # Guardar el video procesado
            final_clip.write_videofile(processed_path, codec='libx264')

        logger.info(f"Video procesado copia existosa")

        
        logger.info(f"Subiendo el archivo procesado al bucket de Google Cloud Storage")
        processed_blob = bucket.blob(f"processed/{processed_filename}")
        processed_blob.upload_from_filename(processed_path)
        logger.info(f"Video procesado subido al bucket en 'processed/{processed_filename}'")
        
        
        # Actualizar el video con la ruta procesada y el estado
        video.processed_path = processed_path
        logger.info("Estado del video actualizado a PROCESSED")

        # Actualizar la tarea a 'PROCESSED'
        task_record.status = TaskStatus.PROCESSED
        db.session.commit()
        logger.info("Estado de la tarea actualizado a PROCESSED")
        
        return {'estado': 'procesado', 'ruta': f"gs://{bucket_name}/processed/{processed_filename}"}
    
    except Exception as e:
        db.session.rollback()
        self.update_state(state='FAILURE', meta={'exc': str(e)})
        if task_record:
            task_record.status = TaskStatus.FAILURE
            db.session.commit()
        logger.error(f"Error al procesar el video: {e}")
        raise