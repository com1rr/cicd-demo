FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

# 使用 Gunicorn 启动 Flask，持续阻塞，兼容 K8s
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.main:app"]