FROM python:3.11-slim

# 필수 라이브러리
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxrandr2 libgbm1 libasound2 \
    libxdamage1 libxshmfence1 libxfixes3 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 크로미움 설치
RUN python -m playwright install chromium

# 소스 복사
COPY . .

# Railway는 $PORT로 리스닝해야 함
ENV PORT=8000
EXPOSE 8000

# uvicorn을 $PORT로 실행
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
