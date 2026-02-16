FROM python:3.9-slim

# Chrome और Chromedriver इंस्टॉल करना
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn से API चालू करना
CMD ["gunicorn", "-b", "0.0.0.0:10000", "main:app"]
