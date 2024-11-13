#FROM python:3.9.17-bookworm
FROM python

WORKDIR /code

COPY  requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install  -r requirements.txt
RUN pip3 install python-dotenv
RUN pip list

COPY  / .

# final configuration
ENV FLASK_APP=app
EXPOSE 8000
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]

