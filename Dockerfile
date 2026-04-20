FROM python:3.9-slim

# सिस्टम डिपेंडेंसी इंस्टॉल करें
RUN apt-get update && apt-get install -y \
    imagemagick \
    ffmpeg \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# इमेजमैजिक पॉलिसी को फिक्स करें (Render के लिए सही पाथ)
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml || sed -i 's/none/read,write/g' /etc/ImageMagick/policy.xml

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "main.py"]

