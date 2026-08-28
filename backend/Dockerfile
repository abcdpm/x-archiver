# 采用你指定的 Python 3.14 极简版基础镜像
FROM python:3.14-slim

WORKDIR /app

# 安装 SQLite 引擎及相关编译依赖
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖清单并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端核心代码
COPY app/ ./app/

# 暴露 FastAPI 服务端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]