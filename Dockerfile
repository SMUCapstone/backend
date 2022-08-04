FROM python:3.10-buster

WORKDIR /usr/src

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

COPY . .

CMD ["python3","-u","app.py"]
