FROM python:3-alpine
MAINTAINER Jonas Als Christensen "jonas.christensen@sesam.io"
RUN apk update
RUN pip3 install --upgrade pip
COPY .requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./service /service
EXPOSE 5000 
CMD ["python3","-u","./service/service.py"]