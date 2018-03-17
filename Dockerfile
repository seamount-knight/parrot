FROM python:3.5.4-alpine
MAINTAINER knight

RUN apk --update add --no-cache mysql-client

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]
EXPOSE 9000
COPY . /app
WORKDIR /app