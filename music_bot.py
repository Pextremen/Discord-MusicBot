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

# Bot prefix and minimal intents
intents = discord.Intents.default()
intents.message_content = True  # Required for commands
bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

# Dictionary for music queues
queues = {}

# Invidious instances - to bypass YouTube bot protection
INVIDIOUS_INSTANCES = [
    'https://invidious.fdn.fr',
    'https://invidious.privacydev.net',
    'https://invidious.lunar.icu',
    'https://iv.melmac.space',
    'https://invidious.slipfox.xyz'
]

# User-Agent rotation list
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
]

# YT-DLP settings - optimized for container environment
def get_ytdl_options(use_cookies=False):
    # Container-optimized user-agent
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    options = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=480]/worst',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        # Optimized for container environment
        'user_agent': user_agent,
        'referer': 'https://www.youtube.com/',
        'sleep_interval': 2,
        'max_sleep_interval': 5,
        'extractor_retries': 5,
        'retries': 5,
        'fragment_retries': 5,
        'extract_flat': False,
        'writethumbnail': False,
        'writeinfojson': False,
        # Container-friendly extraction
        'extractor_args': {
            'youtube': {
                'skip': ['hls', 'dash'],
                'player_client': ['android', 'web'],
                'player_skip': ['webpage'],
            }
        },
        # Minimal headers - container environment
        'http_headers': {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    }
    
    # Cookie support - container environment için optimize
    if use_cookies:
        try:
            # Railway container'da browser yok, cookie'siz çalış
            print("🐳 Container environment - cookie'siz authentication")
        except:
            print("⚠️ Browser cookies bulunamadı - cookie'siz devam ediliyor")
    
    return options

# Ana ytdl instance
ytdl_format_options = get_ytdl_options()

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

async def search_invidious(query, max_results=3):
    """Bypass YouTube bot protection using Invidious API"""
    for instance in INVIDIOUS_INSTANCES:
        try:
            search_url = f"{instance}/api/v1/search"
            params = {
                'q': query,
                'type': 'video',
                'sort_by': 'relevance',
                'duration': 'short,medium,long'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for video in data[:max_results]:
                            if video.get('videoId') and video.get('title'):
                                # Invidious link oluştur
                                invidious_url = f"{instance}/watch?v={video['videoId']}"
                                results.append({
                                    'title': video['title'],
                                    'url': invidious_url,
                                    'youtube_url': f"https://www.youtube.com/watch?v={video['videoId']}",
                                    'duration': video.get('lengthSeconds', 0),
                                    'author': video.get('author', 'Unknown')
                                })
                        
                        if results:
                            print(f"Invidious arama başarılı: {instance}")
                            return results
                        
        except Exception as e:
            print(f"Invidious instance {instance} başarısız: {e}")
            continue
    
    print("Tüm Invidious instances başarısız")
    return []

async def get_spotify_track_info(spotify_url):
    """Extract song information from Spotify links"""
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
        
        # Container environment için multiple format ve client denemesi
        extraction_strategies = [
            {
                'name': 'Android Client',
                'client': ['android'],
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio'
            },
            {
                'name': 'Web Client',
                'client': ['web'],
                'format': 'best[height<=480]/worst'
            },
            {
                'name': 'Basic Format',
                'client': ['android', 'web'],
                'format': 'worst/18'
            }
        ]
        
        for attempt, strategy in enumerate(extraction_strategies):
            try:
                # Strategy-specific options
                ytdl_options = get_ytdl_options(use_cookies=False)
                ytdl_options['format'] = strategy['format']
                ytdl_options['extractor_args']['youtube']['player_client'] = strategy['client']
                
                temp_ytdl = yt_dlp.YoutubeDL(ytdl_options)
                
                print(f"🔍 Deneme {attempt + 1}: {strategy['name']} - {strategy['format']}")
                data = await loop.run_in_executor(None, lambda: temp_ytdl.extract_info(url, download=not stream))
                
                # Veri kontrolü
                if not data:
                    print("❌ Extract_info None döndü")
                    continue
                
                if 'entries' in data:
                    if not data['entries']:
                        print("❌ Entries boş")
                        continue
                    data = data['entries'][0]
                    if not data:
                        print("❌ İlk entry None")
                        continue
                
                if not data.get('url'):
                    print("❌ URL bulunamadı")
                    continue

                filename = data['url'] if stream else temp_ytdl.prepare_filename(data)
                print(f"✅ Başarılı: {data.get('title', 'Unknown')} [{strategy['name']}]")
                return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ {strategy['name']} başarısız: {error_msg[:100]}")
                
                if attempt < len(extraction_strategies) - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    # Son strateji de başarısız
                    raise Exception(f"Tüm extraction stratejileri başarısız: {error_msg}")
        
        raise Exception("Tüm extraction denemeleri başarısız")

@bot.event
async def on_ready():
    print(f'{bot.user} logged in successfully!')

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    """Play music - accepts YouTube links, Spotify links or song names"""
    
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

            # Ana arama denemesi - YouTube + cookies authentication
            player = None
            search_message = await ctx.send("🔍 Aranıyor...")
            
            # İlk önce direkt linkler için deneme
            if query.startswith('http'):
                try:
                    player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
                    if player and player.title:
                        await search_message.edit(content=f"✅ Bulundu: **{player.title}**")
                except Exception as e:
                    print(f"Direkt link başarısız: {e}")
            
            # Arama gerekliyse
            if not player:
                base_query = query.replace("ytsearch:", "").strip()
                
                # YouTube authentication ile arama
                search_attempts = [
                    f"ytsearch1:{base_query}",
                    f"ytsearch3:{base_query}",
                ]
                
                youtube_success = False
                for i, attempt_query in enumerate(search_attempts):
                    try:
                        await search_message.edit(content=f"🔍 YouTube'da aranıyor... ({i+1}/2) [Container Optimized]")
                        player = await YTDLSource.from_url(attempt_query, loop=bot.loop, stream=True)
                        
                        if player and player.title:
                            await search_message.edit(content=f"✅ YouTube'da bulundu: **{player.title}**")
                            youtube_success = True
                            break
                            
                    except Exception as attempt_error:
                        error_msg = str(attempt_error)
                        print(f"⚠️ YouTube arama hatası: {error_msg}")
                        continue
                
                # YouTube başarısızsa Invidious fallback
                if not youtube_success:
                    await search_message.edit(content="🔄 YouTube başarısız! Alternatif arama yapılıyor...")
                    
                    try:
                        invidious_results = await search_invidious(base_query, max_results=3)
                        
                        if invidious_results:
                            for result in invidious_results:
                                try:
                                    await search_message.edit(content=f"🔄 Invidious'tan deneniyor: **{result['title'][:50]}...**")
                                    
                                    # Invidious URL ile dene
                                    player = await YTDLSource.from_url(result['url'], loop=bot.loop, stream=True)
                                    
                                    if player and player.title:
                                        await search_message.edit(content=f"✅ Invidious'tan bulundu: **{player.title}**")
                                        break
                                        
                                except Exception as inv_error:
                                    print(f"Invidious URL başarısız: {inv_error}")
                                    continue
                        else:
                            await search_message.edit(content="❌ Hiçbir arama yöntemi başarılı olmadı")
                            
                    except Exception as invidious_error:
                        print(f"Invidious arama hatası: {invidious_error}")
                        await search_message.edit(content="❌ Alternatif arama da başarısız")
            
            if player is None:
                await search_message.edit(content="❌ Şarkı bulunamadı!")
                await ctx.send("💡 **Öneriler:**\n• Şarkı ismini daha net yazın\n• Sanatçı adını ekleyin\n• İngilizce karakterler kullanın\n• Birkaç dakika bekleyip tekrar deneyin")
                return
            
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                queues[guild_id].append(player)
                await ctx.send(f'**{player.title}** kuyruğa eklendi!')
            else:
                ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
                await ctx.send(f'🎵 Şu an çalıyor: **{player.title}**')

        except Exception as e:
            error_msg = str(e)
            if "Sign in to confirm" in error_msg or "robot" in error_msg.lower():
                await ctx.send("❌ **YouTube bot koruması aktif!**")
                await ctx.send("💡 **Çözüm önerileri:**\n• 5-10 dakika bekleyin ve tekrar deneyin\n• Daha kısa ve basit şarkı isimleri kullanın\n• VPN kullanarak farklı bir konumdan deneyin")
            elif "Tüm extraction stratejileri başarısız" in error_msg:
                await ctx.send("❌ **YouTube extraction başarısız!**")
                await ctx.send("💡 **Sistem durumu:**\n• 3 farklı client stratejisi denendi\n• Invidious backup sistemi de başarısız\n• Container environment optimized\n• 10-15 dakika bekleyip tekrar deneyin")
            elif "Video unavailable" in error_msg or "Video erişilemez" in error_msg:
                await ctx.send("❌ Video mevcut değil veya bölgenizde erişilebilir değil!")
                await ctx.send("💡 Farklı bir video veya şarkı ismi deneyin.")
            elif "Private video" in error_msg:
                await ctx.send("❌ Bu video özel (private) olarak ayarlanmış!")
            elif "age-restricted" in error_msg.lower():
                await ctx.send("❌ Bu video yaş kısıtlaması nedeniyle çalınamıyor!")
            else:
                await ctx.send(f"❌ **Beklenmeyen hata:** {error_msg[:150]}...")
                await ctx.send("💡 Lütfen farklı bir şarkı deneyin veya daha sonra tekrar deneyin.")
                print(f"Play command error: {error_msg}")  # Debug için
                
            # Hata durumunda kuyruktaki bir sonraki şarkıya geç
            if guild_id in queues and queues[guild_id]:
                await ctx.send("🔄 Kuyruktaki sonraki şarkıya geçiliyor...")
                await play_next(ctx)

async def play_next(ctx):
    """Play the next song in queue"""
    guild_id = ctx.guild.id
    if guild_id in queues and queues[guild_id]:
        player = queues[guild_id].popleft()
        ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f'🎵 Şu an çalıyor: **{player.title}**')

@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    """Show the music queue"""
    guild_id = ctx.guild.id
    
    if guild_id not in queues or not queues[guild_id]:
        await ctx.send("📋 Kuyruk boş!")
        return
    
    queue_list = list(queues[guild_id])
    queue_text = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(queue_list[:10])])
    
    if len(queue_list) > 10:
        queue_text += f"\n... ve {len(queue_list) - 10} şarkı daha"
    
    embed = discord.Embed(title="📋 Müzik Kuyruğu", description=queue_text, color=0x0099ff)
    await ctx.send(embed=embed)

@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    """Skip the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Şarkı atlandı!")
    else:
        await ctx.send("❌ Şu anda çalan bir şarkı yok!")

@bot.command(name='stop')
async def stop(ctx):
    """Stop music and clear queue"""
    guild_id = ctx.guild.id
    if guild_id in queues:
        queues[guild_id].clear()
    
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ Müzik durduruldu ve kuyruk temizlendi!")
    else:
        await ctx.send("❌ Bot herhangi bir ses kanalında değil!")

@bot.command(name='pause')
async def pause(ctx):
    """Pause the music"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Müzik duraklatıldı!")
    else:
        await ctx.send("❌ Şu anda çalan bir şarkı yok!")

@bot.command(name='resume')
async def resume(ctx):
    """Resume the music"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Müzik devam ettiriliyor!")
    else:
        await ctx.send("❌ Müzik duraklatılmış değil!")

@bot.command(name='disconnect', aliases=['leave', 'dc'])
async def disconnect(ctx):
    """Botun ses kanalından çıkmasını sağlar"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("🚪 Ses kanalından ayrıldım!")
    else:
        await ctx.send("❌ Zaten herhangi bir ses kanalında değilim!")

@bot.command(name='shuffle')
async def shuffle_queue(ctx):
    """Shuffle the music queue"""
    guild_id = ctx.guild.id
    
    if guild_id not in queues or len(queues[guild_id]) < 2:
        await ctx.send("❌ Karıştırmak için kuyrukte en az 2 şarkı olmalı!")
        return
    
    # Deque'yu listeye çevir, karıştır, tekrar deque yap
    import random
    queue_list = list(queues[guild_id])
    random.shuffle(queue_list)
    queues[guild_id] = deque(queue_list)
    
    await ctx.send("🔀 Kuyruk karıştırıldı!")

@bot.command(name='lyrics', aliases=['lyric'])
async def get_lyrics(ctx, *, query=None):
    """Get song lyrics"""
    if not query:
        if ctx.voice_client and ctx.voice_client.source:
            query = ctx.voice_client.source.title
        else:
            await ctx.send("❌ Şarkı ismi belirtin veya bir şarkı çalın!")
            return
    
    try:
        async with aiohttp.ClientSession() as session:
            # lyrics.ovh API kullan
            search_url = f"https://api.lyrics.ovh/v1/{query}"
            
            async with session.get(search_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    lyrics_text = data.get('lyrics', '')
                    
                    if lyrics_text:
                        # Lyrics çok uzunsa kısalt
                        if len(lyrics_text) > 1900:
                            lyrics_text = lyrics_text[:1900] + "..."
                        
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

@bot.command(name='komutlar', aliases=['commands', 'yardim'])
async def help_command(ctx):
    """Yardım ve komut listesi"""
    embed = discord.Embed(
        title="🎵 Müzik Bot Komutları",
        description="YouTube ve Spotify linklerini destekleyen Discord müzik botu",
        color=0x00ff00
    )
    
    commands_list = [
        ("🎵 `+play [şarkı/link]`", "Şarkı çalar (YouTube/Spotify linki veya şarkı ismi)"),
        ("⏭️ `+skip`", "Şu anki şarkıyı atlar"),
        ("⏸️ `+pause`", "Müziği duraklatır"),
        ("▶️ `+resume`", "Müziği devam ettirir"),
        ("⏹️ `+stop`", "Müziği durdurur ve kuyruğu temizler"),
        ("📋 `+queue`", "Müzik kuyruğunu gösterir"),
        ("🔀 `+shuffle`", "Kuyruğu karıştırır"),
        ("🎤 `+lyrics [şarkı]`", "Şarkı sözlerini gösterir"),
        ("📊 `+status`", "Bot durumu ve istatistikleri"),
        ("🚪 `+disconnect`", "Botun ses kanalından çıkmasını sağlar"),
        ("🧹 `+clear [sayı]`", "Mesajları temizler")
    ]
    
    for name, value in commands_list:
        embed.add_field(name=name, value=value, inline=False)
    
    embed.add_field(
        name="🐳 Container-Optimized System",
        value="• **Multi-Client Strategy:** Android, Web, Basic format fallback\n• **Container Environment:** Railway/Docker için optimize edilmiş\n• **Format Flexibility:** M4A, WebM, MP4 formatları\n• **Invidious Backup:** YouTube başarısızsa alternatif arama",
        inline=False
    )
    
    embed.set_footer(text="Bu bot açık kaynak kodludur ve sürekli geliştirilmektedir.")
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_redirect(ctx):
    """Help komutu yönlendirmesi"""
    await ctx.send("ℹ️ Komut listesi için `+komutlar` yazın!")
    await ctx.send("💡 Alternatifler: `+commands` veya `+yardim`")

@bot.command(name='status', aliases=['durum'])
async def bot_status(ctx):
    """Bot durumu ve istatistikleri"""
    embed = discord.Embed(title="🤖 Bot Durumu", color=0x0099ff)
    
    # Ses kanalı durumu
    if ctx.voice_client:
        if ctx.voice_client.is_playing():
            embed.add_field(name="🎵 Durum", value="Çalıyor", inline=True)
        elif ctx.voice_client.is_paused():
            embed.add_field(name="⏸️ Durum", value="Duraklatıldı", inline=True)
        else:
            embed.add_field(name="⏹️ Durum", value="Durduruldu", inline=True)
            
        embed.add_field(name="📍 Kanal", value=ctx.voice_client.channel.name, inline=True)
    else:
        embed.add_field(name="🚫 Durum", value="Bağlı değil", inline=True)
    
    # Kuyruk durumu
    guild_id = ctx.guild.id
    if guild_id in queues and queues[guild_id]:
        embed.add_field(name="📋 Kuyruk", value=f"{len(queues[guild_id])} şarkı", inline=True)
    else:
        embed.add_field(name="📋 Kuyruk", value="Boş", inline=True)
    
    embed.add_field(name="📊 Sunucu Sayısı", value=f"{len(bot.guilds)}", inline=True)
    embed.add_field(name="👥 Kullanıcı Sayısı", value=f"{len(set(bot.get_all_members()))}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='clear', aliases=['c', 'clean'])
async def clear_messages(ctx, amount: int = 10):
    """Delete specified number of messages (default: 10, max: 100)"""
    
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

# Get bot token from environment variable
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if not TOKEN:
    print("❌ ERROR: DISCORD_BOT_TOKEN environment variable not found!")
    print("💡 Please create a .env file and add your token.")
    print("📖 See README.md for detailed setup instructions.")
    exit(1)

bot.run(TOKEN)