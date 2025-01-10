FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
RUN apt-get update && apt-get install -y --no-install-recommends nginx
RUN pip install  --no-cache-dir beautifulsoup4 fastapi requests uvicorn

# 复制应用代码
COPY . /app
RUN rm -rf /etc/nginx/sites-enabled/default && cp /app/nginx.example.conf /etc/nginx/sites-enabled/default

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;'"]

EXPOSE 80
EXPOSE 8000