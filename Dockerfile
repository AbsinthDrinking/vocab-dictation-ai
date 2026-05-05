# 使用轻量 Python 镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 拷贝项目文件
COPY . /app

# 安装依赖（这里没有额外包，可以留空或者创建 requirements.txt）
# 如果没有 requirements.txt，可以去掉 RUN pip install
RUN pip install --no-cache-dir -r requirements.txt || true

# 容器启动时运行 CLI
CMD ["python", "translation_cli.py"]