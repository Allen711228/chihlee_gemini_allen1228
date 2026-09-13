"""
practice4.py
整合 practice3（Gemini 聯網搜尋最新國際精品新聞）
     + practice2（Telegram 推播架構）
→ 用 Gemini 取得最新精品新聞後，以純文字推播至 Telegram（不傳圖片）
"""

import asyncio
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from telegram import Bot

load_dotenv()

GEMINI_API_KEY   = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN")

# ── 推播目標 ──────────────────────────────────────────────
TARGET_USER_ID  = 8908388815        # 個人（正整數，用戶需先私訊過 Bot）
TARGET_GROUP_ID = "-5522499426"     # 群組（負整數，Bot 需在群組內）
TARGET_CHANNEL  = "-1004343185574"  # 頻道 Chat ID（Bot 需為管理員）


# ── Step 1：用 Gemini 聯網搜尋最新國際精品新聞 ─────────────
def fetch_news_from_gemini(max_retries: int = 3, wait_sec: int = 30) -> str:
    """呼叫 Gemini Google Search Grounding，取得最新國際精品新聞文字。
    遇到 429 配額超限時，自動等待後重試。
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = (
        "請查詢並告訴我今天最新的重要國際精品新聞三則"
        "（包含發生時間與簡要說明），使用繁體中文。"
    )
    print(f"💬 提問：{prompt}\n")
    print("🌐 Gemini 正在自主聯網搜尋最新資料中...")

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )
            print("\n🤖 Gemini 聯網搜尋結果：")
            print(response.text)
            return response.text

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                if attempt < max_retries:
                    print(f"⚠️  API 配額暫時超限，{wait_sec} 秒後重試（第 {attempt}/{max_retries} 次）...")
                    time.sleep(wait_sec)
                else:
                    raise RuntimeError(f"Gemini API 配額超限，已重試 {max_retries} 次仍失敗：{e}") from e
            else:
                raise


# ── Step 2：將文字推播至所有 Telegram 目標 ────────────────
async def send_text(bot: Bot, chat_id: str | int, text: str) -> None:
    """發送純文字訊息至指定 chat_id"""
    await bot.send_message(chat_id=chat_id, text=text)


async def broadcast(bot: Bot, targets: list, message: str) -> None:
    """依序將訊息推播至所有目標"""
    for chat_id in targets:
        print(f"\n📤 推播至目標：{chat_id}")
        try:
            # Telegram 單則訊息上限 4096 字，超過則分段送出
            if len(message) <= 4096:
                await send_text(bot, chat_id, message)
            else:
                chunks = [message[i:i+4096] for i in range(0, len(message), 4096)]
                for idx, chunk in enumerate(chunks, 1):
                    await send_text(bot, chat_id, chunk)
                    print(f"   ✉️  第 {idx}/{len(chunks)} 段已送出")
            print(f"✅ 推播成功：{chat_id}")
        except Exception as e:
            print(f"❌ 推播至 {chat_id} 失敗：{e}")


async def main() -> None:
    # 1. 取得 Gemini 精品新聞
    news_text = fetch_news_from_gemini()

    # 2. 組合推播訊息（加上標題與分隔線）
    message = (
        "🌍 【國際精品新聞快訊】\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + news_text
        + "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
        "📡 資料來源：Gemini Google Search Grounding"
    )

    # 3. 推播至所有目標
    bot = Bot(token=TELEGRAM_TOKEN)
    targets = [TARGET_USER_ID, TARGET_GROUP_ID, TARGET_CHANNEL]
    await broadcast(bot, targets, message)

    print("\n🎉 所有推播任務完成！")


if __name__ == "__main__":
    asyncio.run(main())
