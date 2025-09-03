FROM python:3.10-slim

# playwright 필수 패키지
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxrandr2 libgbm1 libasound2 \
    libxdamage1 libxshmfence1 libxfixes3 xvfb wget gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
# playwright 브라우저 설치
RUN python -m playwright install chromium

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
