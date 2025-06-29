# 🎵 MyDJ26 - Discord Music Bot

**MyDJ26** - Modern Discord music bot with YouTube and Spotify support

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Features

- 🎵 **YouTube and Spotify support** - Play using links or search by song name
- 🎶 **Smart queue system** - Sequential playback and queue management
- ⏯️ **Full playback control** - Pause, resume, skip, stop commands
- 🔀 **Queue shuffling** - Random playback feature
- 📝 **Song lyrics** - Real-time lyrics fetching
- 🧹 **Message cleanup** - Channel management commands
- 🔊 **Auto voice channel management** - Smart connection and switching
- 🛡️ **Error handling** - Comprehensive error catching with user-friendly messages

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- [FFmpeg](https://ffmpeg.org/download.html) (for audio processing)
- Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Pextremen/Discord-DJ.git
   cd Discord-DJ
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
| Command | Alias | Description |
|---------|-------|-------------|
| `+play <song/link>` | `+p` | Plays YouTube/Spotify links or searches by song name |
| `+queue` | `+q` | Shows the music queue |
| `+skip` | `+s` | Skips the current song |
| `+shuffle` | - | Shuffles the queue |
| `+pause` | - | Pauses the music |
| `+resume` | - | Resumes the music |
| `+stop` | - | Stops music and clears queue |
| `+disconnect` | `+leave`, `+dc` | Disconnects from voice channel |

### Other Commands
| Command | Alias | Description |
|---------|-------|-------------|
| `+lyrics [song]` | `+lyric` | Gets song lyrics (leave empty for current song) |
| `+clear [number]` | `+c`, `+clean` | Deletes specified number of messages (default: 10) |

### Usage Examples

```bash
# Play YouTube video
+play https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Play Spotify song
+play https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Search by song name
+play imagine dragons believer

# Queue control
+queue
+skip
+shuffle

# Song lyrics
+lyrics bohemian rhapsody
+lyrics  # (lyrics for currently playing song)
```

## 🛠️ Development

### Project Structure
```
Discord-DJ/
├── music_bot.py          # Main bot file
├── requirements.txt      # Python dependencies
├── env.example          # Example environment file
├── .gitignore           # Git ignore rules
├── Dockerfile           # Docker container definition
├── Procfile             # Heroku deployment
└── README.md            # This file
```

### Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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

## 🐳 Running with Docker

```bash
# Build Docker image
docker build -t mydj26 .

# Run container (requires .env file)
docker run --env-file .env mydj26
```

## ☁️ Deploy to Heroku

1. Create an account on [Heroku](https://heroku.com)
2. Install Heroku CLI
3. In terminal:
   ```bash
   heroku create your-bot-name
   heroku config:set DISCORD_BOT_TOKEN=your_token_here
   git push heroku main
   ```

## 🔧 Troubleshooting

### Common Errors

**"DISCORD_BOT_TOKEN environment variable not found!"**
- Make sure the `.env` file is created correctly
- Verify the token is copied correctly

**"Cannot connect to voice channel"**
- Check bot's voice channel permissions
- Make sure FFmpeg is installed correctly

**"YouTube bot protection is active!"**
- Wait a few minutes and try again
- Try searching by song name instead

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloader
- [FFmpeg](https://ffmpeg.org/) - Audio processing

---

⭐ **If you like this project, don't forget to give it a star!** 