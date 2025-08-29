# Discord TTS Chat Bot

**A voice-enabled Discord bot, mainly developed with ChatGPT.**

當你傳送文字訊息時，若機器人正在語音頻道中，它會自動朗讀訊息內容。

---
## 第一次使用請執行 setup.bat 安裝所需套件
---

## 🔧 指令清單

| 指令 | 說明 |
|------|------|
| `/help` | 顯示此說明訊息 |
| `/join` | 讓機器人加入你的語音頻道 |
| `/leave` | 讓機器人離開語音頻道 |
| `/set_tts [edge/pytts]` | 切換朗讀引擎（Edge TTS 或 pyttsx3） |
| `/allow_others [y/n]` | 是否允許其他使用者使用指令（僅限擁有者） |
| `/shutdown` | 關閉機器人（僅限擁有者） |

---

##  TTS 模式說明

- **edge**：使用微軟雲端的神經網路語音  
   聲音自然、有感情  
   需要網路連線

- **pytts**：使用本地 `pyttsx3` 引擎  
   不需網路連線、速度可調  
   音質較簡單、偏合成音
