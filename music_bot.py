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
    """Extract song information from Spotify links"""
    try:
        # Extract Spotify track ID
        track_id_match = re.search(r'track/([a-zA-Z0-9]+)', spotify_url)
        if not track_id_match:
            return None
        
        track_id = track_id_match.group(1)
        
        # Use Spotify Open Graph API (public, no key required)
        api_url = f"https://open.spotify.com/oembed?url=spotify:track:{track_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Separate artist and song name from title
                    title = data.get('title', '')
                    
                    if ' · ' in title:
                        parts = title.split(' · ')
                        if len(parts) >= 2:
                            song_name = parts[0].strip()
                            artist_name = parts[1].strip()
                            return f"{artist_name} {song_name}"
                    
                    # Fallback: use title as is
                    return title
                    
    except Exception as e:
        print(f"Spotify info extraction error: {e}")
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
    print(f'{bot.user} logged in successfully!')

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    """Plays music - accepts YouTube links, Spotify links or song names"""
    
    if not ctx.author.voice:
        await ctx.send("You must join a voice channel first!")
        return

    channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
        try:
            await ctx.send("Trying to connect to voice channel...")
            voice_client = await channel.connect(timeout=60.0, reconnect=True)
            await ctx.send(f"✅ Successfully connected to {channel.name}!")
        except Exception as e:
            await ctx.send(f"❌ Cannot connect to voice channel: {str(e)}")
            await ctx.send("💡 Solutions:\n- Try a different voice channel\n- Change server voice region\n- Check bot's voice channel permissions")
            return
    elif ctx.voice_client.channel != channel:
        try:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"✅ Moved to {channel.name}!")
        except Exception as e:
            await ctx.send(f"❌ Could not switch channel: {str(e)}")
            return

    guild_id = ctx.guild.id
    if guild_id not in queues:
        queues[guild_id] = deque()

    async with ctx.typing():
        try:
            # Search Spotify links on YouTube
            if 'spotify.com' in query:
                await ctx.send("🎵 Spotify link detected, extracting song info...")
                
                # Get song info from Spotify
                track_info = await get_spotify_track_info(query)
                
                if track_info:
                    await ctx.send(f"🔍 Searching YouTube for **{track_info}**...")
                    query = f"ytsearch:{track_info}"
                else:
                    await ctx.send("❌ Could not extract Spotify song info. Please try typing the song name.")
                    return
                    
            elif not query.startswith('http'):
                # If it's a song name, search on YouTube
                query = f"ytsearch:{query}"

            player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
            
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                queues[guild_id].append(player)
                await ctx.send(f'**{player.title}** added to queue!')
            else:
                ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
                await ctx.send(f'Now playing: **{player.title}**')

        except Exception as e:
            error_msg = str(e)
            if "Sign in to confirm" in error_msg or "robot" in error_msg.lower():
                await ctx.send("❌ YouTube bot protection is active! Please wait a few minutes and try again.")
                await ctx.send("💡 **Alternative:** Try typing the song name: `+play imagine dragons believer`")
            elif "Video unavailable" in error_msg:
                await ctx.send("❌ Video is unavailable or not accessible in your region!")
            elif "Private video" in error_msg:
                await ctx.send("❌ This video is set to private!")
            elif "age-restricted" in error_msg.lower():
                await ctx.send("❌ This video cannot be played due to age restrictions!")
            else:
                await ctx.send(f"❌ An error occurred: {error_msg[:100]}...")
                
            # In case of error, move to next song in queue
            if guild_id in queues and queues[guild_id]:
                await ctx.send("🔄 Moving to next song in queue...")
                await play_next(ctx)

async def play_next(ctx):
    """Play the next song in queue"""
    guild_id = ctx.guild.id
    
    if guild_id in queues and queues[guild_id]:
        next_player = queues[guild_id].popleft()
        ctx.voice_client.play(next_player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f'Now playing: **{next_player.title}**')

@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    """Show the music queue"""
    guild_id = ctx.guild.id
    
    if guild_id not in queues or not queues[guild_id]:
        await ctx.send("Queue is empty!")
        return
    
    queue_list = []
    for i, player in enumerate(list(queues[guild_id])[:10], 1):
        queue_list.append(f"{i}. {player.title}")
    
    embed = discord.Embed(title="Music Queue", description="\n".join(queue_list), color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    """Skip the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Song skipped!")
    else:
        await ctx.send("No song is currently playing!")

@bot.command(name='stop')
async def stop(ctx):
    """Stop the music and clear the queue"""
    guild_id = ctx.guild.id
    
    if guild_id in queues:
        queues[guild_id].clear()
    
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Music stopped and queue cleared!")

@bot.command(name='pause')
async def pause(ctx):
    """Pause the music"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Music paused!")
    else:
        await ctx.send("No song is currently playing!")

@bot.command(name='resume')
async def resume(ctx):
    """Resume the music"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Music resumed!")
    else:
        await ctx.send("Music is already playing or not paused!")

@bot.command(name='disconnect', aliases=['leave', 'dc'])
async def disconnect(ctx):
    """Disconnect bot from voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel!")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command(name='shuffle')
async def shuffle_queue(ctx):
    """Shuffle the music queue"""
    guild_id = ctx.guild.id
    
    if guild_id not in queues or not queues[guild_id]:
        await ctx.send("❌ Queue is empty, nothing to shuffle!")
        return
    
    if len(queues[guild_id]) < 2:
        await ctx.send("❌ Need at least 2 songs to shuffle!")
        return
    
    # Shuffle the queue
    import random
    queue_list = list(queues[guild_id])
    random.shuffle(queue_list)
    queues[guild_id] = deque(queue_list)
    
    await ctx.send(f"🔀 Queue shuffled! ({len(queue_list)} songs)")

@bot.command(name='lyrics', aliases=['lyric'])
async def get_lyrics(ctx, *, query=None):
    """Get song lyrics"""
    
    # If no query, use currently playing song
    if not query:
        if ctx.voice_client and ctx.voice_client.source:
            if hasattr(ctx.voice_client.source, 'title'):
                query = ctx.voice_client.source.title
            else:
                await ctx.send("❌ Currently playing song not found. Type the song name: `+lyrics imagine dragons believer`")
                return
        else:
            await ctx.send("❌ No song is currently playing. Type the song name: `+lyrics imagine dragons believer`")
            return
    
    try:
        await ctx.send(f"🔍 Searching lyrics for **{query}**...")
        
        # Use Lyrics API (free)
        async with aiohttp.ClientSession() as session:
            # Lyrics.ovh API (free, simple)
            api_url = f"https://api.lyrics.ovh/v1/{query.replace(' ', '%20')}"
            
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    lyrics_text = data.get('lyrics', '')
                    
                    if lyrics_text:
                        # Discord character limit: 2000
                        if len(lyrics_text) > 1900:
                            lyrics_text = lyrics_text[:1900] + "\n\n**... (check web for full lyrics)**"
                        
                        embed = discord.Embed(
                            title=f"🎵 {query}",
                            description=f"```{lyrics_text}```",
                            color=0x1DB954
                        )
                        embed.set_footer(text="Powered by lyrics.ovh")
                        await ctx.send(embed=embed)
                        return
                
                # If API fails, show alternative message
                await ctx.send(f"❌ Lyrics not found for **{query}**!")
                await ctx.send("💡 **Tip:** Include artist name: `+lyrics imagine dragons believer`")
                
    except asyncio.TimeoutError:
        await ctx.send("❌ Lyrics search timed out!")
    except Exception as e:
        await ctx.send(f"❌ Error occurred while fetching lyrics: {str(e)[:100]}...")

@bot.command(name='clear', aliases=['c', 'clean'])
async def clear_messages(ctx, amount: int = 10):
    """Delete specified number of messages (default: 10, max: 100)"""
    
    # Permission check
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ You need 'Manage Messages' permission to use this command!")
        return
    
    # Amount check
    if amount < 1:
        await ctx.send("❌ Number of messages to delete must be at least 1!")
        return
    elif amount > 100:
        await ctx.send("❌ You can delete a maximum of 100 messages at once!")
        return
    
    try:
        # Delete messages (include bot command message)
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        # Success message (will be deleted after 5 seconds)
        success_msg = await ctx.send(f"✅ {len(deleted)-1} messages deleted successfully!")
        await asyncio.sleep(5)
        await success_msg.delete()
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to delete messages!")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Error occurred while deleting messages: {str(e)}")

# Get your bot token from environment variable
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if not TOKEN:
    print("❌ ERROR: DISCORD_BOT_TOKEN environment variable not found!")
    print("💡 Please create a .env file and add your token.")
    print("📖 See README.md for detailed setup instructions.")
    exit(1)

bot.run(TOKEN)