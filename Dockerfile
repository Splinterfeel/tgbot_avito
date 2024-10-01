FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/
RUN python3 -m pip install -r requirements.txt
COPY ./*.py ./

ENTRYPOINT [ "python3", "tgbot.py" ]
