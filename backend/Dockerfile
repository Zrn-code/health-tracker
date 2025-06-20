# 使用官方 Python 基礎映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製需求檔與應用程式
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# 設定環境變數
ENV PORT=8080

# 開放 port
EXPOSE 8080

# 執行應用程式
CMD ["python", "app.py"]

