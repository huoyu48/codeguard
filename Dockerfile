# 阶段 1：构建（安装依赖）
FROM python:3.11-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install -e ".[dev]"

# 阶段 2：运行（只拷贝产物，镜像更小）
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ app/
COPY tests/ tests/

EXPOSE 8000

# 默认启动 FastAPI 服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
