# Python 3.11 base image
FROM python:3.11-slim

# Sistem paketlerini güncelle ve FFmpeg kur
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Requirements dosyasını kopyala ve kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Bot'u çalıştır
CMD ["python", "music_bot.py"] 