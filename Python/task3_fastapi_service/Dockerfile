FROM python:3.9

WORKDIR /task3_fastapi_sevice

COPY . .

RUN pip install -r requirements.txt

RUN chmod +x docker/*.sh



#WORKDIR src

#CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000