FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENV PORT=8080
EXPOSE 8080

# ✅ 使用 Gunicorn 來穩定監聽 Cloud Run 的 $PORT
CMD ["gunicorn", "-b", ":8080", "app:app"]
