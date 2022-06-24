FROM python:3-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "app.py", "/data"]
