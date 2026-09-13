#國堂_LV名牌包_打到骨折_channel
#-4322810613

import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot, InputMediaPhoto

load_dotenv()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# 設定不同推播目標
TARGET_USER_ID = 8908388815              # 個人 (正整數，用戶需先私訊過 Bot)
TARGET_GROUP_ID = "-5522499426"         # 群組 (負整數，Bot 需在群組內)
TARGET_CHANNEL = "-1004343185574"     # 頻道 Chat ID (Bot 需為管理員)

# ── 推播設定 ──────────────────────────────────────────────
# 文字訊息
TEXT_MESSAGE = "📢 大家好！這是來自 Telegram Bot 的跨平台主動推播通知。"

# 圖片來源：填入本機路徑 或 公開 URL，留空字串表示不傳圖片
# 範例（本機檔案）：IMAGE_SOURCE = "images/banner.jpg"
# 範例（網路圖片）：IMAGE_SOURCE = "https://example.com/photo.jpg"
IMAGE_SOURCE = ""          # ← 修改此處以傳送圖片

# 圖片說明文字（caption），若不需要可留空
IMAGE_CAPTION = "🖼️ 商品圖片說明"
# ─────────────────────────────────────────────────────────


async def send_text(bot: Bot, chat_id: str | int, message: str):
    """發送純文字訊息"""
    await bot.send_message(chat_id=chat_id, text=message)


async def send_photo(bot: Bot, chat_id: str | int, photo: str, caption: str = ""):
    """發送圖片（可附說明文字）
    photo 可以是：
      - 本機檔案路徑（str），例如 'images/banner.jpg'
      - 公開圖片 URL（str），例如 'https://example.com/photo.jpg'
    """
    if photo.startswith("http://") or photo.startswith("https://"):
        # 網路圖片直接傳 URL
        await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
    else:
        # 本機圖片以二進位方式讀取後上傳
        with open(photo, "rb") as f:
            await bot.send_photo(chat_id=chat_id, photo=f, caption=caption)


async def broadcast(chat_id: str | int, message: str, image_source: str = "", caption: str = ""):
    """對單一目標發送文字（＋圖片）"""
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        if image_source:
            # 有圖片：傳送圖片並把文字放入 caption；若 caption 為空則改用 message
            effective_caption = caption if caption else message
            await send_photo(bot, chat_id, image_source, effective_caption)
            print(f"✅ 成功發送圖片至：{chat_id}")
        else:
            # 無圖片：只傳送文字
            await send_text(bot, chat_id, message)
            print(f"✅ 成功發送文字至：{chat_id}")
    except Exception as e:
        print(f"❌ 發送至 {chat_id} 失敗：{e}")


async def main():
    # 可同時推送給多個目標
    targets = [
        TARGET_USER_ID,
        TARGET_GROUP_ID,
        TARGET_CHANNEL,
    ]

    for chat_id in targets:
        await broadcast(
            chat_id,
            message=TEXT_MESSAGE,
            image_source=IMAGE_SOURCE,
            caption=IMAGE_CAPTION,
        )

if __name__ == "__main__":
    asyncio.run(main())