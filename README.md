# 🎵 MyDJ26 - Discord Müzik Botu

**MyDJ26** - YouTube ve Spotify destekli modern Discord müzik botu

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Özellikler

- 🎵 **YouTube ve Spotify desteği** - Hem link hem de şarkı ismi ile arama
- 🎶 **Akıllı kuyruk sistemi** - Sıralı çalma ve kuyruk yönetimi
- ⏯️ **Tam çalma kontrolü** - Pause, resume, skip, stop komutları
- 🔀 **Kuyruk karıştırma** - Rastgele çalma özelliği
- 📝 **Şarkı sözleri** - Anlık şarkı sözü getirme
- 🧹 **Mesaj temizleme** - Kanal düzenleme komutları
- 🔊 **Otomatik ses kanalı yönetimi** - Akıllı bağlantı ve geçiş
- 🛡️ **Hata yönetimi** - Kapsamlı hata yakalama ve kullanıcı dostu mesajlar

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.8 veya üzeri
- [FFmpeg](https://ffmpeg.org/download.html) (ses işleme için)
- Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))

### Kurulum

1. **Projeyi klonlayın:**
   ```bash
   git clone https://github.com/yourusername/MyDJ26.git
   cd MyDJ26
   ```

2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment dosyasını oluşturun:**
   ```bash
   cp env.example .env
   ```

4. **Discord Bot Token'ınızı ekleyin:**
   - `.env` dosyasını açın
   - `your_discord_bot_token_here` yazan yere gerçek token'ınızı yazın
   ```
   DISCORD_BOT_TOKEN=YOUR_ACTUAL_TOKEN_HERE
   ```

5. **Botu çalıştırın:**
   ```bash
   python music_bot.py
   ```

## 🎮 Komutlar

### Müzik Komutları
| Komut | Kısayol | Açıklama |
|-------|---------|----------|
| `+play <şarkı/link>` | `+p` | YouTube/Spotify linkini çalar veya şarkı ismi arar |
| `+queue` | `+q` | Müzik kuyruğunu gösterir |
| `+skip` | `+s` | Şu anki şarkıyı atlar |
| `+shuffle` | - | Kuyruğu karıştırır |
| `+pause` | - | Müziği duraklatır |
| `+resume` | - | Müziği devam ettirir |
| `+stop` | - | Müziği durdurur ve kuyruğu temizler |
| `+disconnect` | `+leave`, `+dc` | Ses kanalından ayrılır |

### Diğer Komutlar
| Komut | Kısayol | Açıklama |
|-------|---------|----------|
| `+lyrics [şarkı]` | `+lyric` | Şarkı sözlerini getirir (boş bırakılırsa çalan şarkının) |
| `+clear [sayı]` | `+c`, `+clean` | Belirtilen sayıda mesajı siler (varsayılan: 10) |

### Kullanım Örnekleri

```bash
# YouTube video çalma
+play https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Spotify şarkısı çalma
+play https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Şarkı ismi ile arama
+play imagine dragons believer

# Kuyruk kontrolü
+queue
+skip
+shuffle

# Şarkı sözleri
+lyrics bohemian rhapsody
+lyrics  # (şu an çalan şarkının sözleri)
```

## 🛠️ Geliştirme

### Proje Yapısı
```
MyDJ26/
├── music_bot.py          # Ana bot dosyası
├── requirements.txt      # Python bağımlılıkları
├── env.example          # Örnek environment dosyası
├── .gitignore           # Git ignore kuralları
├── Dockerfile           # Docker container tanımı
├── Procfile             # Heroku deployment
└── README.md            # Bu dosya
```

### Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📋 Discord Bot Kurulumu

1. [Discord Developer Portal](https://discord.com/developers/applications)'a gidin
2. "New Application" butonuna tıklayın
3. Uygulamanıza bir isim verin
4. "Bot" sekmesine gidin
5. "Add Bot" butonuna tıklayın
6. "Token" bölümünden token'ınızı kopyalayın
7. "Privileged Gateway Intents" altında "Message Content Intent"'i aktif edin

### Bot İzinleri
Botunuzu sunucuya eklerken şu izinlere ihtiyaç vardır:
- ✅ Send Messages
- ✅ Connect (Ses kanallarına bağlanma)
- ✅ Speak (Ses kanallarında konuşma)
- ✅ Use Voice Activity
- ✅ Manage Messages (clear komutu için)

## 🐳 Docker ile Çalıştırma

```bash
# Docker image oluştur
docker build -t mydj26 .

# Container çalıştır (.env dosyası gerekli)
docker run --env-file .env mydj26
```

## ☁️ Deploy (Heroku)

1. [Heroku](https://heroku.com)'da hesap oluşturun
2. Heroku CLI'yi yükleyin
3. Terminal'de:
   ```bash
   heroku create your-bot-name
   heroku config:set DISCORD_BOT_TOKEN=your_token_here
   git push heroku main
   ```

## 🔧 Sorun Giderme

### Yaygın Hatalar

**"DISCORD_BOT_TOKEN environment variable'ı bulunamadı!"**
- `.env` dosyasının doğru oluşturulduğundan emin olun
- Token'ın doğru kopyalandığından emin olun

**"Ses kanalına bağlanamıyorum"**
- Bot'un ses kanalı izinlerini kontrol edin
- FFmpeg'in doğru yüklendiğinden emin olun

**"YouTube bot koruması aktif!"**
- Birkaç dakika bekleyin ve tekrar deneyin
- Şarkı ismini yazarak deneyin

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video indirici
- [FFmpeg](https://ffmpeg.org/) - Ses işleme

---

⭐ **Bu projeyi beğendiyseniz star vermeyi unutmayın!** 