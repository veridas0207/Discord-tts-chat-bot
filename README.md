# Discord-tts-chat-bot

**mainly developed with ChatGPT**

**傳送文字訊息時，機器人會自動朗讀內容（若在語音頻道中）**


**機器人指令清單**
/help - 顯示此說明訊息
/join - 讓機器人加入你的語音頻道
/leave - 讓機器人離開語音頻道
/set_tts [edge/pytts] - 切換朗讀引擎（Edge TTS 或 pyttsx3)
/allow_others [y/n] - 是否允許其他使用者使用指令（僅限擁有者）
/shutdown - 關閉機器人（僅限擁有者）

**TTS 模式說明**
• edge - 使用微軟雲端的神經網路語音，聲音自然且有感情，需網路連線
• pytts - 使用本地 pyttsx3 引擎，速度可調且不需網路，但音質較簡單
