# aio-pika-sandbox

sandbox for experiments with pika and rabbitmq

## Initial setup

1. create and activate virtual environment
```shell
python3 -m venv venv
source venv/bin/activate
```
2. create environment variables file
```shell
cat > .env << _EOF_
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=adminsecret
RABBITMQ_DEFAULT_VHOST=hello
_EOF_

export (cat .env| xargs)
```
3. create docker instance of rabbitmq
```shell
docker run -d -p 15672:15672 -p 5672:5672 \
  --name aio-pika-rabbit --hostname aio-pika-rabbit \
  --env-file .env rabbitmq:3.8.14-management-alpine
```
4. install packages from `requirements.txt`
```shell
pip install -r requirements.txt
```
5. run app server
```shell
python app.py
```
6. go to browser and open link send http://localhost:8080/send
7. run receiver part `receive.py`
```shell
python receive.py
```
