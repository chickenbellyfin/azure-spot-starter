FROM python:3-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENV APP_LOG_DIR=/var/log
ENTRYPOINT ["python3", "app.py", "/data"]
