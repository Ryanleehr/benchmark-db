# 基础镜像：官方 Python 3.12 精简版
FROM python:3.12-slim

# 容器内的工作目录
WORKDIR /app
ENV TZ=Asia/Shanghai
ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app/src

# 先只复制依赖清单
COPY requirements.txt .

# 安装依赖（用清华镜像加速）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 再复制项目代码
COPY src/ ./src/
COPY data/companies.csv ./data/
COPY data/headcount.csv ./data/

# 声明服务端口
EXPOSE 8000

# 容器启动时执行的命令
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]