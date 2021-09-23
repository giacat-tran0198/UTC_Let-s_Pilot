# pull official base image
FROM python:3.8.3-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat

# install dependencies
COPY requirements.txt /
RUN pip install -r /requirements.txt

# copy project
WORKDIR /server
ADD . /server

# permissions file
RUN chmod 755 entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/server/entrypoint.sh"]