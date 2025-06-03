import discord
from discord.ext import commands
import edge_tts
import pyttsx3
import asyncio
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uuid

################ 初始化 ################
# 你的 USER ID
DC_USER_ID = 
# 你的 BOT TOKEN
DC_BOT_TOKEN = ''
# 預設其他人不能用
ALLOW_OTHERS = False

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)
#########################################


################ cache cleaner ################
TTS_CACHE_DIR = "tts_cache"
os.makedirs(TTS_CACHE_DIR, exist_ok=True)  # 確保資料夾存在

cache_cleaner_scheduler = AsyncIOScheduler()

def clean_tts_files():
    now = datetime.now()
    cutoff = now - timedelta(minutes=1)

    for fname in os.listdir(TTS_CACHE_DIR):
        # 確保只刪除 .mp3 且以 tts_ 開頭的檔案
        if fname.endswith(".mp3") and fname.startswith("tts_"):
            path = os.path.join(TTS_CACHE_DIR, fname)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                if mtime < cutoff:
                    os.remove(path)
                    print(f"🧹 已刪除過期檔案: {fname}")
            except Exception as e:
                print(f"❌ 刪除檔案失敗: {fname}, 錯誤: {e}")

#########################################



################ 啟動事件迴圈 ################
@bot.event
async def on_ready():
    print(f"✅ Bot 已登入為 {bot.user}")

    try:
        if not cache_cleaner_scheduler.running:
            cache_cleaner_scheduler.add_job(clean_tts_files, "interval", minutes=5)  # 每 5 分鐘執行一次
            cache_cleaner_scheduler.start()
            print("🕒 清理排程器已啟動")
    except Exception as e:
        print(f"❌ 啟動排程器失敗: {e}")

    try:
        synced = await bot.tree.sync()
        print(f"同步了以下 Slash Commands：")
        for cmd in synced:
            print(f" - {cmd.name}")
    except Exception as e:
        print(f"同步 Slash Commands 出錯: {e}")
#########################################


################ tts ################
# 預設使用 edge-tts
TTS_MODE = "edge"

# edge-tts
async def generate_edge_tts(text: str, filename: str = None):
    if filename is None:
        filename = os.path.join(TTS_CACHE_DIR, f"tts_{uuid.uuid4().hex}.mp3")
    communicate = edge_tts.Communicate(
        text=text,
        voice="zh-TW-YunJheNeural",
        rate="+0%"
    )
    await communicate.save(filename)
    return filename

# pyttsx3
pyttsx3_engine = None

def init_pyttsx3():
    global pyttsx3_engine
    pyttsx3_engine = pyttsx3.init()
    pyttsx3_engine.setProperty('rate', 175) # 語速（words per minute）
    pyttsx3_engine.setProperty('volume', 1.0) # 音量（0.0~1.0）

def generate_pyttsx3_tts(text: str, filename: str = None):
    global pyttsx3_engine
    if pyttsx3_engine is None:
        init_pyttsx3()

    if filename is None:
        filename = os.path.join(TTS_CACHE_DIR, f"tts_{uuid.uuid4().hex}.mp3")
    pyttsx3_engine.save_to_file(text, filename)
    pyttsx3_engine.runAndWait()
    return filename

def close_pyttsx3():
    global pyttsx3_engine
    if pyttsx3_engine is not None:
        try:
            pyttsx3_engine.stop()
        except Exception:
            pass
        pyttsx3_engine = None

# tts switch function
def switch_tts_mode(new_mode: str):
    global TTS_MODE
    if new_mode == TTS_MODE:
        return  # 沒切換不用動

    # 如果舊模式是 pyttsx3，要關閉引擎
    if TTS_MODE == "pytts":
        close_pyttsx3()

    # 切換模式
    TTS_MODE = new_mode

    # 如果新模式是 pyttsx3，要初始化引擎
    if TTS_MODE == "pytts":
        init_pyttsx3()

# 運作
@bot.event
async def on_message(message):
    if message.author == bot.user or message.content.startswith('/'):
        return

    # 🔒 判斷權限
    if not ALLOW_OTHERS and message.author.id != DC_USER_ID:
        return

    voice_client = message.guild.voice_client
    if voice_client:
        text = message.content.strip()
        if not text:
            return

        # 使用統一的 TTS 函式
        if TTS_MODE == "edge":
            filename = await generate_edge_tts(text)
        elif TTS_MODE == "pytts":
            filename = generate_pyttsx3_tts(text)
        else:
            filename = await generate_edge_tts(text)

        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio(source=filename))

        await message.channel.send(f"📢 正在朗讀：{text}")
#########################################


################ bot 指令 ################
# 允許其他使用者在 ALLOW_OTHERS = True 時使用的指令清單
ALLOWED_COMMANDS_FOR_OTHERS = {
    "join", "leave", "help", "set_tts"
}
def is_user_allowed(interaction: discord.Interaction, command_name: str) -> bool:
    if interaction.user.id == DC_USER_ID:
        return True
    return ALLOW_OTHERS and command_name in ALLOWED_COMMANDS_FOR_OTHERS

@bot.tree.command(name="help", description="顯示指令說明")
async def slash_help(interaction: discord.Interaction):
    if not is_user_allowed(interaction, "help"):
        await interaction.response.send_message("❌ 你沒有權限使用此指令。", ephemeral=True)
        return
    help_text = (
        "🤖 **語音朗讀機器人指令清單**\n\n"
        "/help - 顯示此說明訊息\n"
        "/join - 讓機器人加入你的語音頻道\n"
        "/leave - 讓機器人離開語音頻道\n"
        "/set_tts [edge/pytts] - 切換朗讀引擎（Edge TTS 或 pyttsx3）\n"
        "/allow_others [y/n] - 是否允許其他使用者使用指令（僅限擁有者）\n"
        "/shutdown - 關閉機器人（僅限擁有者）\n\n"
        "💬 傳送文字訊息時，機器人會自動朗讀內容（若在語音頻道中）\n\n"
        "🗣️ **TTS 模式說明**\n"
        "• edge - 使用微軟雲端的神經網路語音，聲音自然且有感情，需網路連線\n"
        "• pytts - 使用本地 pyttsx3 引擎，速度可調且不需網路，但音質較簡單\n"
    )
    await interaction.response.send_message(help_text, ephemeral=True)

@bot.tree.command(name="allow_others", description="設定是否允許其他使用者觸發語音")
async def slash_allow_others(interaction: discord.Interaction, mode: str):
    global ALLOW_OTHERS
    if interaction.user.id != DC_USER_ID:
        await interaction.response.send_message("❌ 你沒有權限使用此指令。", ephemeral=True)
        return
    if mode.lower() in ["y", "yes"]:
        ALLOW_OTHERS = True
        await interaction.response.send_message("😊 已允許其他使用者使用 TTS")
    elif mode.lower() in ["n", "no"]:
        ALLOW_OTHERS = False
        await interaction.response.send_message("😭 已禁止其他使用者使用 TTS")
    else:
        await interaction.response.send_message("❌ 格式錯誤，請使用 'y' 或 'n'", ephemeral=True)

@bot.tree.command(name="set_tts", description="切換 TTS 模式（edge 或 pytts）")
async def slash_set_tts(interaction: discord.Interaction, mode: str):
    if not is_user_allowed(interaction, "set_tts"):
        await interaction.response.send_message("❌ 你沒有權限使用此指令。", ephemeral=True)
        return
    if mode not in ["edge", "pytts"]:
        await interaction.response.send_message("❌ 模式只能是 'edge' 或 'pytts'", ephemeral=True)
        return

    switch_tts_mode(mode)
    await interaction.response.send_message(f"✅ TTS 模式已切換為：{mode}")

@bot.tree.command(name="join", description="讓機器人加入你的語音頻道")
async def slash_join(interaction: discord.Interaction):
    if not is_user_allowed(interaction, "join"):
        await interaction.response.send_message("❌ 你沒有權限使用此指令。", ephemeral=True)
        return
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message("🎤 已加入語音頻道")
    else:
        await interaction.response.send_message("❌ 你不在語音頻道", ephemeral=True)

@bot.tree.command(name="leave", description="讓機器人離開語音頻道")
async def slash_leave(interaction: discord.Interaction):
    if not is_user_allowed(interaction, "leave"):
        await interaction.response.send_message("❌ 你沒有權限使用此指令。", ephemeral=True)
        return
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 已離開語音頻道")
    else:
        await interaction.response.send_message("❌ 我不在語音頻道", ephemeral=True)

@bot.tree.command(name="shutdown", description="關閉機器人")
async def slash_shutdown(interaction: discord.Interaction):
    if interaction.user.id != DC_USER_ID:
        await interaction.response.send_message("❌ 你沒有權限使用此指令。", ephemeral=True)
        return
    await interaction.response.send_message("🛑 Bot 即將關閉…")
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
    await bot.close()
#########################################

################ main function ################
try:
    bot.run(DC_BOT_TOKEN)
except Exception as e:
    print(f"錯誤：{e}")
#########################################
