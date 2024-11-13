
Entorno
———————————
python3 -m venv venv
source venv/bin/activate

Requirements

pip install -r requirements.txt 

flask run

Correr FastAPI

uvicorn src.main:app –-reload
http://localhost:8000/docs


quebe
celery -A worker.celery_worker.celery worker --pool=solo --loglevel=info
celery -A worker.celery_worker.celery flower

Correr pruebas unitarias
python -m unittest discover -s tests/unit

para  ejecutar entornos locales 
export FLASK_ENV=local && flask run  
export FLASK_ENV=local && python3 app.py

para  ejecutar entornos productivos 
export FLASK_ENV=production && flask run  
export FLASK_ENV=production && python3 app.py

Arquitectura del balanceador de cargas - observabilidad - infraestructura

Infraestructura
Las maquinas se instancian automaticamente a partir del manejador de grupo de instancias configurado a partir de la plantilla que contiene el siguiente bash: 
#!/bin/bash
sudo su
apt-get update
apt-get install -y git
rm -rf /home/ubuntu/fpv_enthusiast_tour_idrl
git clone https://gitlab.com/cloud_computing7370641/fpv_enthusiast_tour_idrl.git /home/ubuntu/fpv_enthusiast_tour_idrl
cd /home/ubuntu/fpv_enthusiast_tour_idrl
git checkout feature/balanceo-cargas
git pull origin feature/balanceo-cargas
apt-get -y install python3-venv	
python3 -m venv venv
source venv/bin/activate
apt-get -y install python3-pip
pip install -r requirements.txt
export FLASK_ENV=production
python3 app.py &
celery -A worker.celery_worker.celery worker --pool=solo --loglevel=info &
celery -A worker.celery_worker.celery flower

Esto permite que la instancia se aprovisione y ejecute cada uno los demonios requeridos como la cola, celery, flower y flask.

Las cuentas de servicio configuradas para la instancia de base de datos y el IAM son las siguientes: 

1065233496528-compute@developer.gserviceaccount.com --> Cloud Storage con roles de admin, propietario y admin object storage.
cuenta-servicio-base-datos-fpv@fpv-enthusiast-tour-idrl.iam.gserviceaccount.com --> Base de datos con roles de admin.
instancia-base-datos-fpv-idrl --> Instancia de base de datos en posgresql 15.8

En cuanto al manejador de instancias, tiene una politicia de health check con tiempo espera de 5 segundos, de mal estado de 10 errores respectivamente. Este maneja se habilita por el puerto 5000, tanto el umbral de buen y mal estado son de 2.

En cuanto a los detalles del escalamiento automático se tiene minimo 1 instancia y maximo 3, tiempo de espera para incializacion y aprovisamiento de maquina 60 segundos, utilizacion de la CPU para hacer autoescalamiento 60%.

Balanceador de cargas 
-Configracion de frontend del balanceador de cargas: Ip externa 34.49.93.230 ---> (name:api-rest-lb-rule) 
-Configuracion de backend del balanceador: Verificacion de estado check igual que el monitor --> (name:instance-group-server-api-rest) y Backend --> (name:api-rest-backend-service)

Redes, subredes y politicas de Firewall
Redes de VPC -->(name:vpc-zonal-network-fpv-idrl) es una red regional que se extiende al este de norteamerica aproximadamente en el estado de Virginia con subred us-east-1 
Subred interna -->(name: subnet-east) y el CIDR (name: 10.142.0.0/21).
Reglas de Firewall --> Se definieron 10 reglas en las cuales incluyen alojamiento de trafico externo e interna, SSH, RDP, ICMP, 5000, 80, 8080 y health check.

Storage Cloud
Se tiene un bucket tiene lo siguiente 
-Cuenta de servicio (1065233496528-compute@developer.gserviceaccount.com) 
-Nombre (name:bucket-videos-fpv-idrl)
-URL (name:gs://bucket-videos-fpv-idrl)
-Regional en us-east-1.
-Storage key: .json parate del respositorio

API-Rest
Se instanciaron dos ambientes tanto para local como para producccion las cuales son xport FLASK_ENV=local y FLASK_ENV=produccion




