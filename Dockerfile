FROM python:3.9-slim

# ज़रूरी टूल्स और ब्राउज़र इनस्टॉल करना
RUN apt-get update && apt-get install -y \
    wget gnupg unzip chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 120 सेकंड का टाइमआउट और 1 वर्कर ताकि RAM पर लोड न पड़े
CMD ["gunicorn", "--timeout", "120", "--workers", "1", "--threads", "2", "-b", "0.0.0.0:10000", "main:app"]
