# 🎵 MyDJ26 - Advanced Discord Music Bot

**MyDJ26** - Modern Discord music bot with YouTube and Spotify support, featuring YouTube bot protection bypass and container optimization.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🔥 Latest Major Update

### ✨ What's New in This Release:

#### 🛡️ YouTube Bot Protection Solutions
- **🔄 Invidious Backup System** - Automatically switches to alternative YouTube frontends when main YouTube fails
- **🤖 Multi-Client Strategy** - Tries Android, Web, and Basic clients for maximum compatibility
- **🔀 User-Agent Rotation** - Uses different browser identities to avoid detection
- **🐳 Container Optimization** - Specially optimized for Railway/Docker cloud deployment

#### 🔒 Security & Code Quality Improvements
- **❌ Removed Hardcoded Tokens** - All sensitive data now uses environment variables
- **🌐 International Code Standards** - Comments and documentation converted to English
- **🛠️ Enhanced Error Handling** - Specific solutions for each error type
- **📝 Professional Documentation** - Comprehensive README with troubleshooting guides

#### 🌐 User Experience Enhancements
- **International Interface** - Full English interface with Turkish command aliases
- **📊 Advanced Status Command** - Detailed bot statistics with `+status`
- **❓ Comprehensive Help System** - Complete command guide with `+commands`
- **🔄 Smart Fallback System** - Automatically tries next method when one fails
- **🇹🇷 Turkish Command Support** - Turkish aliases for all commands (e.g., `+cal` for `+play`)

#### 🎵 Music Features
- **📝 Enhanced Lyrics System** - Integration with lyrics.ovh API
- **⏭️ Smart Queue Management** - Continues to next song on errors
- **🎶 Multiple Format Support** - M4A, WebM, MP4 compatibility
- **🔊 Improved Audio Quality** - Better audio extraction strategies

> 🚀 **Ready for Production**: This update makes the bot significantly more reliable against YouTube restrictions and ready for cloud deployment!

## ✨ Features

### 🚀 Core Features
- 🎵 **YouTube and Spotify support** - Play using links or search by song name
- 🎶 **Smart queue system** - Sequential playback and advanced queue management
- ⏯️ **Full playback control** - Pause, resume, skip, stop commands
- 🔀 **Queue shuffling** - Random playback feature
- 📝 **Song lyrics** - Real-time lyrics fetching from lyrics.ovh API
- 🧹 **Message cleanup** - Channel management commands
- 🔊 **Auto voice channel management** - Smart connection and switching

### 🛡️ YouTube Bot Protection Bypass
- **🔄 Invidious Backup System** - Alternative servers when YouTube fails
- **🤖 Multi-Client Strategy** - Android, Web, and Basic client attempts
- **🔀 User-Agent Rotation** - Different browser identities
- **🐳 Container Optimization** - Specially optimized for Railway/Docker

### 🌐 Advanced Features
- **🇹🇷 Turkish Interface** - Full Turkish user interface support
- **📊 Bot Status** - Detailed bot statistics with `+status` command
- **❓ Help System** - Comprehensive help menu with `+komutlar`
- **🛡️ Smart Error Handling** - Each error type has specific solution suggestions
- **🔄 Automatic Fallback** - If one method fails, try the next
- **⏭️ Queue Management** - Continue to next song on error

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- [FFmpeg](https://ffmpeg.org/download.html) (for audio processing)
- Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/MyDJ26.git
   cd MyDJ26
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file:**
   ```bash
   cp env.example .env
   ```

4. **Add your Discord Bot Token:**
   - Open the `.env` file
   - Replace `your_discord_bot_token_here` with your actual token
   ```
   DISCORD_BOT_TOKEN=YOUR_ACTUAL_TOKEN_HERE
   ```

5. **Run the bot:**
   ```bash
   python music_bot.py
   ```

## 🎮 Commands

### Music Commands
| Command | Aliases | Description |
|---------|---------|-------------|
| `+play <song/link>` | `+p`, `+cal`, `+oynat` | Plays YouTube/Spotify links or searches by song name |
| `+queue` | `+q`, `+kuyruk` | Shows the music queue |
| `+skip` | `+s`, `+atla` | Skips the current song |
| `+shuffle` | `+karistir` | Shuffles the queue |
| `+pause` | `+dur` | Pauses the music |
| `+resume` | `+devam` | Resumes the music |
| `+stop` | `+durdur` | Stops music and clears queue |
| `+disconnect` | `+leave`, `+dc`, `+ayril` | Disconnects from voice channel |

### Utility Commands
| Command | Aliases | Description |
|---------|---------|-------------|
| `+lyrics [song]` | `+lyric`, `+sozler` | Gets song lyrics (leave empty for current song) |
| `+status` | `+durum` | Shows bot status and statistics |
| `+commands` | `+help`, `+komutlar`, `+yardim` | Shows command list and help |
| `+clear [number]` | `+c`, `+clean`, `+temizle` | Deletes specified number of messages (default: 10) |

### Usage Examples

```bash
# Play YouTube video (English/Turkish)
+play https://www.youtube.com/watch?v=dQw4w9WgXcQ
+cal https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Play Spotify song
+play https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Search by song name (English/Turkish)
+play imagine dragons believer
+oynat imagine dragons believer

# Queue control (English/Turkish)
+queue / +kuyruk
+skip / +atla
+shuffle / +karistir

# Music control (English/Turkish)
+pause / +dur
+resume / +devam
+stop / +durdur

# Song lyrics (English/Turkish)
+lyrics bohemian rhapsody / +sozler bohemian rhapsody
+lyrics  # (lyrics for currently playing song)

# Bot status and help (English/Turkish)
+status / +durum
+commands / +komutlar
```

## 🛠️ Advanced Configuration

### YouTube Bot Protection Solutions

This bot includes several strategies to handle YouTube's bot detection:

1. **Invidious Instances** - Uses alternative YouTube frontends
2. **Multiple Extraction Strategies** - Tries different clients (Android, Web)
3. **Format Flexibility** - Supports M4A, WebM, MP4 formats
4. **Container Environment** - Optimized for Docker/Railway deployment

### Invidious Instances Used:
- `https://invidious.fdn.fr`
- `https://invidious.privacydev.net`
- `https://invidious.lunar.icu`
- `https://iv.melmac.space`
- `https://invidious.slipfox.xyz`

## 🐳 Running with Docker

```bash
# Build Docker image
docker build -t mydj26 .

# Run container (requires .env file)
docker run --env-file .env mydj26
```

## ☁️ Deploy to Railway

Railway is a modern cloud platform that makes deployment simple and fast.

1. **Create a Railway account:**
   - Go to [Railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub:**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect it's a Python project

3. **Add Environment Variables:**
   - In your Railway project dashboard
   - Go to "Variables" tab
   - Add: `DISCORD_BOT_TOKEN` = `your_actual_token_here`

4. **Deploy:**
   - Railway will automatically build and deploy your bot
   - Your bot will be live in seconds!

### Railway Features:
- ✅ **Automatic deploys** - Pushes to main branch auto-deploy
- ✅ **Free tier** - Great for small bots
- ✅ **Easy scaling** - Upgrade when needed
- ✅ **Built-in monitoring** - Logs and metrics included

## 📋 Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give your application a name
4. Go to the "Bot" tab
5. Click "Add Bot"
6. Copy the token from the "Token" section
7. Enable "Message Content Intent" under "Privileged Gateway Intents"

### Bot Permissions
When adding the bot to your server, it needs these permissions:
- ✅ Send Messages
- ✅ Connect (to voice channels)
- ✅ Speak (in voice channels)
- ✅ Use Voice Activity
- ✅ Manage Messages (for clear command)

## 🔧 Troubleshooting

### Common Errors

**"DISCORD_BOT_TOKEN environment variable not found!"**
- Make sure the `.env` file is created correctly
- Verify the token is copied correctly without quotes

**"YouTube bot protection is active!"**
- Wait 5-10 minutes and try again
- Use shorter and simpler song names
- Try using VPN from different location
- The bot will automatically try Invidious instances

**"Cannot connect to voice channel"**
- Check bot's voice channel permissions
- Make sure FFmpeg is installed correctly
- Try different voice channel
- Check server voice region settings

**"All extraction strategies failed"**
- 3 different client strategies were attempted
- Invidious backup system also failed
- Wait 10-15 minutes and try again
- YouTube may be experiencing heavy restrictions

## 🛠️ Development

### Project Structure
```
MyDJ26/
├── music_bot.py          # Main bot file
├── requirements.txt      # Python dependencies
├── env.example          # Example environment file
├── .gitignore           # Git ignore rules
├── Dockerfile           # Docker container definition
├── Procfile             # Railway deployment
└── README.md            # This file
```

### Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [Invidious](https://github.com/iv-org/invidious) - Alternative YouTube frontend
- [lyrics.ovh](https://lyrics.ovh) - Lyrics API service

## 📊 Stats

- 🎵 **Multi-format support**: M4A, WebM, MP4
- 🔄 **5 Invidious instances** for reliability
- 🤖 **3 extraction strategies** for YouTube
- 🇹🇷 **Full Turkish interface** support
- 🐳 **Container optimized** for cloud deployment 