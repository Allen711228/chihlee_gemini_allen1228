#PS5 夏日遊戲精選

import asyncio
import os
from PIL import Image
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# ── 推播目標 ──────────────────────────────────────────────
TARGET_USER_ID  = 8908388815        # 個人 (正整數，用戶需先私訊過 Bot)
TARGET_GROUP_ID = "-5522499426"     # 群組 (負整數，Bot 需在群組內)
TARGET_CHANNEL  = "-1004343185574"  # 頻道 Chat ID (Bot 需為管理員)

# ── 推播內容設定 ──────────────────────────────────────────
TEXT_MESSAGE = "🎮 PS5 遊戲最新特賣資訊，快來看看！"

# assets 資料夾路徑（自動掃描所有圖片）
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# 支援的圖片副檔名（avif 會自動轉為 jpg 後上傳）
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}

# 各圖片對應設定：caption 說明文字 + 點擊按鈕連結
# 格式：
#   "檔名": {
#       "caption" : "說明文字（支援 HTML）",
#       "buttons" : [{"text": "按鈕文字", "url": "https://..."}]
#   }
IMAGE_CONFIG: dict[str, dict] = {
    "images.jpg": {
        "caption": "🎮 <b>PS5 遊戲精選</b>\n立即前往官網選購！",
        "buttons": [
            {"text": "🛒 前往 PS5 官網", "url": "https://www.playstation.com/zh-hant-tw/ps5/"},
        ],
    },
    "34d92099d34fe590796ed034cc22334fd25127c4.jpg": {
        "caption": "🎮 <b>PS5 特賣活動</b>\n限時優惠，手刀搶購！",
        "buttons": [
            {"text": "🔥 查看特賣活動", "url": "https://store.playstation.com/zh-hant-tw/"},
        ],
    },
    "ps5_action.jpg": {
        "caption": "⚔️ <b>動作冒險</b> — 未來城市戰場",
        "buttons": [
            {"text": "🕹️ 購買遊戲", "url": "https://store.playstation.com/zh-hant-tw/"},
        ],
    },
    "ps5_rpg.jpg": {
        "caption": "🐉 <b>RPG</b> — 奇幻世界史詩冒險",
        "buttons": [
            {"text": "🕹️ 購買遊戲", "url": "https://store.playstation.com/zh-hant-tw/"},
        ],
    },
    "ps5_racing.jpg": {
        "caption": "🏎️ <b>競速</b> — 霓虹城市夜間賽道",
        "buttons": [
            {"text": "🕹️ 購買遊戲", "url": "https://store.playstation.com/zh-hant-tw/"},
        ],
    },
    "ps5_horror.jpg": {
        "caption": "👻 <b>恐怖生存</b> — 鬼屋探險",
        "buttons": [
            {"text": "🕹️ 購買遊戲", "url": "https://store.playstation.com/zh-hant-tw/"},
        ],
    },
    "ps5_sports.jpg": {
        "caption": "⚽ <b>運動</b> — 萬人體育場實況",
        "buttons": [
            {"text": "🕹️ 購買遊戲", "url": "https://store.playstation.com/zh-hant-tw/"},
        ],
    },
}
# ─────────────────────────────────────────────────────────


def get_image_files(folder: str) -> list[str]:
    """掃描資料夾，回傳所有圖片的完整路徑（依檔名排序）"""
    if not os.path.isdir(folder):
        return []
    return [
        os.path.join(folder, f)
        for f in sorted(os.listdir(folder))
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    ]


def convert_to_jpg_if_needed(img_path: str) -> str:
    """若圖片為 avif 等非 Telegram 原生格式，轉換成 jpg 後回傳新路徑"""
    ext = os.path.splitext(img_path)[1].lower()
    if ext in {".avif"}:
        jpg_path = os.path.splitext(img_path)[0] + "_converted.jpg"
        if not os.path.exists(jpg_path):
            print(f"🔄 轉換格式：{os.path.basename(img_path)} → jpg")
            with Image.open(img_path) as im:
                im.convert("RGB").save(jpg_path, "JPEG", quality=90)
        return jpg_path
    return img_path


def build_keyboard(buttons: list[dict]) -> InlineKeyboardMarkup | None:
    """依設定建立 InlineKeyboard，每個按鈕各佔一列"""
    if not buttons:
        return None
    rows = [[InlineKeyboardButton(b["text"], url=b["url"])] for b in buttons]
    return InlineKeyboardMarkup(rows)


async def send_text(bot: Bot, chat_id: str | int, message: str):
    """發送純文字訊息"""
    await bot.send_message(chat_id=chat_id, text=message)


async def send_photo_with_link(
    bot: Bot,
    chat_id: str | int,
    photo: str,
    caption: str = "",
    keyboard: InlineKeyboardMarkup | None = None,
):
    """發送圖片，附說明文字（HTML）與可點擊連結按鈕"""
    send_path = convert_to_jpg_if_needed(photo)
    with open(send_path, "rb") as f:
        await bot.send_photo(
            chat_id=chat_id,
            photo=f,
            caption=caption,
            parse_mode="HTML",          # 支援 <b>, <a href="..."> 等 HTML 標籤
            reply_markup=keyboard,      # 圖片下方連結按鈕
        )


async def broadcast_to_target(bot: Bot, chat_id: str | int, image_files: list[str]):
    """對單一目標依序發送所有圖片（含連結按鈕）；無圖片時改發純文字"""
    if not image_files:
        try:
            await send_text(bot, chat_id, TEXT_MESSAGE)
            print(f"✅ 文字已發送至：{chat_id}")
        except Exception as e:
            print(f"❌ 發送文字至 {chat_id} 失敗：{e}")
        return

    for img_path in image_files:
        filename = os.path.basename(img_path)
        config   = IMAGE_CONFIG.get(filename, {})
        caption  = config.get("caption", TEXT_MESSAGE)
        keyboard = build_keyboard(config.get("buttons", []))
        try:
            await send_photo_with_link(bot, chat_id, img_path, caption, keyboard)
            print(f"✅ [{filename}] 已發送至：{chat_id}")
        except Exception as e:
            print(f"❌ [{filename}] 發送至 {chat_id} 失敗：{e}")


async def main():
    image_files = get_image_files(ASSETS_DIR)
    if image_files:
        print(f"📂 找到 {len(image_files)} 張圖片：{[os.path.basename(f) for f in image_files]}")
    else:
        print("⚠️  assets 資料夾中無圖片，將改為發送純文字")

    bot = Bot(token=TELEGRAM_TOKEN)

    targets = [
        TARGET_USER_ID,
        TARGET_GROUP_ID,
        TARGET_CHANNEL,
    ]

    for chat_id in targets:
        print(f"\n📤 推播至目標：{chat_id}")
        await broadcast_to_target(bot, chat_id, image_files)


if __name__ == "__main__":
    asyncio.run(main())
