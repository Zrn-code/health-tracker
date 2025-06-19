# 使用官方 Python 基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製需求檔與應用程式
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 建立非 root 使用者
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 設定環境變數
ENV PORT=8080
ENV FLASK_APP=app.py

# 開放 port
EXPOSE 8080

# 執行應用程式 (綁定到所有介面)
CMD ["python", "-c", "import app; app.app.run(host='0.0.0.0', port=8080)"]