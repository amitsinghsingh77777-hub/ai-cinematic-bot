FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    imagemagick \
    ffmpeg \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's/policy domain="path" rights="none" pattern="@\*"/policy domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml || true

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "main.py"]
