FROM python:3.9-slim

# ज़रूरी टूल्स इंस्टॉल करें
RUN apt-get update && apt-get install -y \
    imagemagick \
    ffmpeg \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "main.py"]
