import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import re
import aiohttp
from collections import deque
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Bot prefix'i ve minimal intents
intents = discord.Intents.default()
intents.message_content = True  # Komutlar için gerekli
bot = commands.Bot(command_prefix='+', intents=intents)

# Müzik kuyruğu için sözlük
queues = {}

# YT-DLP ayarları - YouTube bot koruması için güncellenmiş
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    # YouTube bot koruması için ek ayarlar
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'referer': 'https://www.youtube.com/',
    'sleep_interval': 1,
    'max_sleep_interval': 5,
    'sleep_interval_subtitles': 1,
    'extractor_retries': 3,
    'retries': 3,
    'fragment_retries': 3,
    'extract_flat': False,
    'writethumbnail': False,
    'writeinfojson': False,
    'ignoreerrors': True,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

async def get_spotify_track_info(spotify_url):
    """Spotify linkinden şarkı bilgilerini çıkarır"""
    try:
        # Spotify track ID'sini çıkar
        track_id_match = re.search(r'track/([a-zA-Z0-9]+)', spotify_url)
        if not track_id_match:
            return None
        
        track_id = track_id_match.group(1)
        
        # Spotify Open Graph API kullan (public, key gerektirmez)
        api_url = f"https://open.spotify.com/oembed?url=spotify:track:{track_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Title'dan sanatçı ve şarkı ismini ayır
                    title = data.get('title', '')
                    
                    if ' · ' in title:
                        parts = title.split(' · ')
                        if len(parts) >= 2:
                            song_name = parts[0].strip()
                            artist_name = parts[1].strip()
                            return f"{artist_name} {song_name}"
                    
                    # Fallback: title'ı olduğu gibi kullan
                    return title
                    
    except Exception as e:
        print(f"Spotify bilgi çıkarma hatası: {e}")
        return None
    
    return None

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    """Müzik çalar - YouTube linki, Spotify linki veya şarkı ismi kabul eder"""
    
    if not ctx.author.voice:
        await ctx.send("Önce bir ses kanalına katılmalısın!")
        return

    channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
        try:
            await ctx.send("Ses kanalına bağlanmaya çalışıyorum...")
            voice_client = await channel.connect(timeout=60.0, reconnect=True)
            await ctx.send(f"✅ {channel.name} kanalına başarıyla bağlandım!")
        except Exception as e:
            await ctx.send(f"❌ Ses kanalına bağlanamıyorum: {str(e)}")
            await ctx.send("💡 Çözüm önerileri:\n- Farklı bir ses kanalı deneyin\n- Sunucu voice region'ını değiştirin\n- Botun ses kanalı izinlerini kontrol edin")
            return
    elif ctx.voice_client.channel != channel:
        try:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"✅ {channel.name} kanalına taşındım!")
        except Exception as e:
            await ctx.send(f"❌ Kanal değiştirilemedi: {str(e)}")
            return

    guild_id = ctx.guild.id
    if guild_id not in queues:
        queues[guild_id] = deque()

    async with ctx.typing():
        try:
            # Spotify linklerini YouTube'da arama
            if 'spotify.com' in query:
                await ctx.send("🎵 Spotify linki algılandı, şarkı bilgileri çıkarılıyor...")
                
                # Spotify'dan şarkı bilgilerini al
                track_info = await get_spotify_track_info(query)
                
                if track_info:
                    await ctx.send(f"🔍 **{track_info}** YouTube'da aranıyor...")
                    query = f"ytsearch:{track_info}"
                else:
                    await ctx.send("❌ Spotify şarkı bilgileri alınamadı. Lütfen şarkı ismini yazarak deneyin.")
                    return
                    
            elif not query.startswith('http'):
                # Şarkı ismi ise YouTube'da ara
                query = f"ytsearch:{query}"

            player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
            
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                queues[guild_id].append(player)
                await ctx.send(f'**{player.title}** kuyruğa eklendi!')
            else:
                ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
                await ctx.send(f'Şu an çalıyor: **{player.title}**')

        except Exception as e:
            error_msg = str(e)
            if "Sign in to confirm" in error_msg or "robot" in error_msg.lower():
                await ctx.send("❌ YouTube bot koruması aktif! Lütfen birkaç dakika bekleyin ve tekrar deneyin.")
                await ctx.send("💡 **Alternatif:** Şarkı ismini yazarak deneyin: `+play imagine dragons believer`")
            elif "Video unavailable" in error_msg:
                await ctx.send("❌ Video mevcut değil veya bölgenizde erişilebilir değil!")
            elif "Private video" in error_msg:
                await ctx.send("❌ Bu video özel (private) olarak ayarlanmış!")
            elif "age-restricted" in error_msg.lower():
                await ctx.send("❌ Bu video yaş kısıtlaması nedeniyle çalınamıyor!")
            else:
                await ctx.send(f"❌ Hata oluştu: {error_msg[:100]}...")
                
            # Hata durumunda kuyruktaki bir sonraki şarkıya geç
            if guild_id in queues and queues[guild_id]:
                await ctx.send("🔄 Kuyruktaki sonraki şarkıya geçiliyor...")
                await play_next(ctx)

async def play_next(ctx):
    """Kuyrukta bir sonraki şarkıyı çal"""
    guild_id = ctx.guild.id
    
    if guild_id in queues and queues[guild_id]:
        next_player = queues[guild_id].popleft()
        ctx.voice_client.play(next_player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f'Şu an çalıyor: **{next_player.title}**')

@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    """Müzik kuyruğunu göster"""
    guild_id = ctx.guild.id
    
    if guild_id not in queues or not queues[guild_id]:
        await ctx.send("Kuyruk boş!")
        return
    
    queue_list = []
    for i, player in enumerate(list(queues[guild_id])[:10], 1):
        queue_list.append(f"{i}. {player.title}")
    
    embed = discord.Embed(title="Müzik Kuyruğu", description="\n".join(queue_list), color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    """Şu anki şarkıyı atla"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Şarkı atlandı!")
    else:
        await ctx.send("Şu an çalan bir şarkı yok!")

@bot.command(name='stop')
async def stop(ctx):
    """Müziği durdur ve kuyruğu temizle"""
    guild_id = ctx.guild.id
    
    if guild_id in queues:
        queues[guild_id].clear()
    
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Müzik durduruldu ve kuyruk temizlendi!")

@bot.command(name='pause')
async def pause(ctx):
    """Müziği duraklat"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Müzik duraklatıldı!")
    else:
        await ctx.send("Şu an çalan bir şarkı yok!")

@bot.command(name='resume')
async def resume(ctx):
    """Müziği devam ettir"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Müzik devam ediyor!")
    else:
        await ctx.send("Müzik zaten çalıyor veya duraklatılmış değil!")

@bot.command(name='disconnect', aliases=['leave', 'dc'])
async def disconnect(ctx):
    """Botun ses kanalından ayrılması"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Ses kanalından ayrıldım!")
    else:
        await ctx.send("Zaten bir ses kanalında değilim!")

@bot.command(name='shuffle')
async def shuffle_queue(ctx):
    """Müzik kuyruğunu karıştırır"""
    guild_id = ctx.guild.id
    
    if guild_id not in queues or not queues[guild_id]:
        await ctx.send("❌ Kuyruk boş, karıştırılacak şarkı yok!")
        return
    
    if len(queues[guild_id]) < 2:
        await ctx.send("❌ Karıştırmak için en az 2 şarkı gerekli!")
        return
    
    # Kuyruğu karıştır
    import random
    queue_list = list(queues[guild_id])
    random.shuffle(queue_list)
    queues[guild_id] = deque(queue_list)
    
    await ctx.send(f"🔀 Kuyruk karıştırıldı! ({len(queue_list)} şarkı)")

@bot.command(name='lyrics', aliases=['lyric'])
async def get_lyrics(ctx, *, query=None):
    """Şarkı sözlerini getirir"""
    
    # Eğer query yoksa, çalan şarkıyı kullan
    if not query:
        if ctx.voice_client and ctx.voice_client.source:
            if hasattr(ctx.voice_client.source, 'title'):
                query = ctx.voice_client.source.title
            else:
                await ctx.send("❌ Şu an çalan şarkı bulunamadı. Şarkı ismini yazın: `+lyrics imagine dragons believer`")
                return
        else:
            await ctx.send("❌ Şu an çalan şarkı yok. Şarkı ismini yazın: `+lyrics imagine dragons believer`")
            return
    
    try:
        await ctx.send(f"🔍 **{query}** için şarkı sözleri aranıyor...")
        
        # Lyrics API kullan (ücretsiz)
        async with aiohttp.ClientSession() as session:
            # Lyrics.ovh API (ücretsiz, basit)
            api_url = f"https://api.lyrics.ovh/v1/{query.replace(' ', '%20')}"
            
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    lyrics_text = data.get('lyrics', '')
                    
                    if lyrics_text:
                        # Discord karakter limiti: 2000
                        if len(lyrics_text) > 1900:
                            lyrics_text = lyrics_text[:1900] + "\n\n**... (devamı için web'den bakın)**"
                        
                        embed = discord.Embed(
                            title=f"🎵 {query}",
                            description=f"```{lyrics_text}```",
                            color=0x1DB954
                        )
                        embed.set_footer(text="Powered by lyrics.ovh")
                        await ctx.send(embed=embed)
                        return
                
                # API başarısız olursa alternatif mesaj
                await ctx.send(f"❌ **{query}** için şarkı sözleri bulunamadı!")
                await ctx.send("💡 **İpucu:** Sanatçı adını da ekleyin: `+lyrics imagine dragons believer`")
                
    except asyncio.TimeoutError:
        await ctx.send("❌ Şarkı sözleri araması zaman aşımına uğradı!")
    except Exception as e:
        await ctx.send(f"❌ Şarkı sözleri getirilirken hata oluştu: {str(e)[:100]}...")

@bot.command(name='clear', aliases=['c', 'clean'])
async def clear_messages(ctx, amount: int = 10):
    """Belirtilen miktarda mesajı siler (varsayılan: 10, maksimum: 100)"""
    
    # İzin kontrolü
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ Bu komutu kullanmak için 'Mesajları Yönet' izniniz olmalı!")
        return
    
    # Miktar kontrolü
    if amount < 1:
        await ctx.send("❌ Silinecek mesaj sayısı en az 1 olmalı!")
        return
    elif amount > 100:
        await ctx.send("❌ Tek seferde en fazla 100 mesaj silebilirsiniz!")
        return
    
    try:
        # Mesajları sil (bot komut mesajını da dahil et)
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        # Başarı mesajı (5 saniye sonra silinecek)
        success_msg = await ctx.send(f"✅ {len(deleted)-1} mesaj başarıyla silindi!")
        await asyncio.sleep(5)
        await success_msg.delete()
        
    except discord.Forbidden:
        await ctx.send("❌ Mesajları silmek için yeterli iznim yok!")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Mesajlar silinirken hata oluştu: {str(e)}")

# Botunuzun token'ını environment variable'dan al
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if not TOKEN:
    print("❌ HATA: DISCORD_BOT_TOKEN environment variable'ı bulunamadı!")
    print("💡 Lütfen .env dosyasını oluşturun ve token'ınızı ekleyin.")
    print("📖 Detaylı kurulum için README.md dosyasına bakın.")
    exit(1)

bot.run(TOKEN)