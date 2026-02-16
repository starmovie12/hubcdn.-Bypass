FROM python:3.9-slim

# Chrome और Chromedriver इनस्टॉल करना
RUN apt-get update && apt-get install -y \
    wget gnupg unzip chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Timeout बढ़ाकर 120 सेकंड किया गया है ताकि 'Worker Timeout' न आए
CMD ["gunicorn", "--timeout", "120", "--workers", "1", "--threads", "2", "-b", "0.0.0.0:10000", "main:app"]
