"""
practice5.py
同時抓取多個來源的消費者物價指數（CPI），整合成報告後推播至 Telegram。

資料來源：
  1. 台灣 & 美國 & 全球主要國家 — IMF DataMapper API（無需 API Key）
  2. 全球主要國家補充             — World Bank Open Data（無需 API Key）
"""

import asyncio
import os
from datetime import datetime

import requests
import yfinance as yf
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# ── 推播目標 ──────────────────────────────────────────────
TARGET_USER_ID  = 8908388815
TARGET_GROUP_ID = "-5288505693"
TARGET_CHANNEL  = "-1004428854154"

TIMEOUT = 20  # requests 超時秒數


# ════════════════════════════════════════════════════════════
# 1. IMF DataMapper — 台灣、美國及全球主要國家 CPI 年增率
#    指標：PCPIPCH = Inflation rate, average consumer prices (% change)
#    API 文件：https://www.imf.org/external/datamapper/api/v1/
# ════════════════════════════════════════════════════════════

IMF_COUNTRIES = {
    "TWN": "🇹🇼 台灣",
    "USA": "🇺🇸 美國",
    "JPN": "🇯🇵 日本",
    "CHN": "🇨🇳 中國",
    "DEU": "🇩🇪 德國",
    "GBR": "🇬🇧 英國",
    "KOR": "🇰🇷 韓國",
    "AUS": "🇦🇺 澳洲",
    "FRA": "🇫🇷 法國",
    "SGP": "�� 新加坡",
}

# 顯示近幾年資料
SHOW_YEARS = ["2022", "2023", "2024", "2025", "2026"]


def fetch_imf_cpi() -> str:
    """
    從 IMF DataMapper API 取得各國 CPI 年增率（%）
    回傳格式化字串
    """
    codes = ",".join(IMF_COUNTRIES.keys())
    url = f"https://www.imf.org/external/datamapper/api/v1/PCPIPCH/{codes}"

    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        raw = resp.json()
        country_data = raw.get("values", {}).get("PCPIPCH", {})

        lines = [
            "📊 【IMF CPI 通膨率年增率（%）】",
            f"{'國家':<12}" + "  ".join(f"{y:>6}" for y in SHOW_YEARS),
            "─" * 52,
        ]

        for code, label in IMF_COUNTRIES.items():
            data = country_data.get(code, {})
            row_vals = []
            for yr in SHOW_YEARS:
                v = data.get(yr)
                if v is not None:
                    row_vals.append(f"{float(v):>6.1f}")
                else:
                    row_vals.append(f"{'—':>6}")
            lines.append(f"{label:<12}" + "  ".join(row_vals))

        lines.append("")
        lines.append("  * 2025、2026 為 IMF 預測值")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ IMF CPI 抓取失敗：{e}"


# ════════════════════════════════════════════════════════════
# 2. World Bank — 全球主要國家 CPI 指數（非年增率，絕對值）
#    指標：FP.CPI.TOTL，基期 2010=100
# ════════════════════════════════════════════════════════════

WB_COUNTRIES = {
    "JP": "🇯🇵 日本",
    "US": "🇺🇸 美國",
    "CN": "🇨🇳 中國",
    "DE": "🇩🇪 德國",
    "GB": "🇬🇧 英國",
    "KR": "🇰🇷 韓國",
    "AU": "🇦🇺 澳洲",
    "FR": "🇫🇷 法國",
    "SG": "🇸🇬 新加坡",
}


def fetch_wb_country(code: str, name: str) -> str:
    """抓取單一國家 World Bank CPI 指數（最近 3 年）"""
    url = (
        f"https://api.worldbank.org/v2/country/{code}"
        f"/indicator/FP.CPI.TOTL?format=json&mrv=3"
    )
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
        if len(payload) < 2 or not payload[1]:
            return f"  {name}：無資料"

        parts = []
        for entry in payload[1]:
            yr  = entry.get("date", "—")
            val = entry.get("value")
            if val is not None:
                parts.append(f"{yr}:{round(val, 1)}")

        return f"  {name:<12}" + "  ".join(parts) if parts else f"  {name}：無資料"

    except Exception as e:
        return f"  {name}：抓取失敗（{e}）"


def fetch_worldbank_cpi() -> str:
    """抓取全球主要國家 World Bank CPI 絕對指數（基期 2010=100）"""
    lines = [
        "🌍 【World Bank CPI 指數（基期 2010=100，近 3 年）】",
        "─" * 44,
    ]
    for code, name in WB_COUNTRIES.items():
        lines.append(fetch_wb_country(code, name))
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════
# 3. 國際能源現貨/期貨報價 — Yahoo Finance（yfinance）
#    不需 API Key，資料接近即時（延遲約 15 分鐘）
# ════════════════════════════════════════════════════════════

ENERGY_TICKERS = {
    # ── 原油期貨 ─────────────────────────────────────
    "CL=F": ("🛢️  WTI 原油",          "美元/桶"),
    "BZ=F": ("🛢️  Brent 原油",        "美元/桶"),
    # ── 天然氣期貨 ───────────────────────────────────
    "NG=F": ("🔥 天然氣 Henry Hub",    "美元/MMBtu"),
    # ── 煤礦：美國/全球動力煤 ────────────────────────
    "BTU":  ("⛏️  Peabody Energy（美國動力煤）",      "美元/股"),
    "AMR":  ("⛏️  Alpha Metallurgical（美國冶金煤）", "美元/股"),
    "HCC":  ("⛏️  Warrior Met Coal（美國冶金煤）",    "美元/股"),
    # ── 煤礦：亞太市場 proxy（中國/印尼進口基準）────
    "METC": ("⛏️  Ramaco Resources（亞太冶金煤 proxy）", "美元/股"),
    # ── 煤礦：歐洲市場 proxy（俄羅斯替代市場基準）──
    "COKE": ("⛏️  SunCoke Energy（歐洲焦煤 proxy）",  "美元/股"),
}


def fetch_energy_prices() -> str:
    """使用 yfinance 抓取原油、天然氣、煤礦最新報價"""
    lines = [
        "⚡ 【國際能源價格（Yahoo Finance，延遲約 15 分鐘）】",
        "─" * 44,
    ]

    for ticker, (name, unit) in ENERGY_TICKERS.items():
        try:
            hist = yf.Ticker(ticker).history(period="5d")
            if hist.empty:
                lines.append(f"  {name}：無資料")
                continue
            close = hist["Close"].dropna()
            price = close.iloc[-1]
            date  = close.index[-1].strftime("%Y-%m-%d")
            # 計算近 5 日漲跌
            if len(close) >= 2:
                chg     = price - close.iloc[-2]
                chg_pct = chg / close.iloc[-2] * 100
                arrow   = "▲" if chg >= 0 else "▼"
                chg_str = f"{arrow}{abs(chg_pct):.2f}%"
            else:
                chg_str = "—"
            lines.append(f"  {name}")
            lines.append(f"    {price:.2f} {unit}  {chg_str}  ({date})")
        except Exception as e:
            lines.append(f"  {name}：抓取失敗（{e}）")

    lines.append("")
    lines.append("  * 煤礦以主要上市煤礦公司股價參考（無直接煤礦期貨）")
    lines.append("  * 亞太 proxy 反映中國/印尼進口市場；歐洲 proxy 反映俄煤替代市場")
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════
# 4. Alpha Vantage — 煤礦均價、天然氣月資料
#    demo key 可用：NATURAL_GAS、COAL（月頻率）
#    申請免費正式 key：https://www.alphavantage.co/support/#api-key
# ════════════════════════════════════════════════════════════

AV_API_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "demo")  # 有正式 key 可加入 .env

AV_COMMODITIES = {
    "NATURAL_GAS": ("🔥 天然氣均價（Henry Hub）", "美元/MMBtu"),
    "BRENT":       ("🛢️  Brent 原油月均價",        "美元/桶"),
    "COAL":        ("⛏️  全球煤礦均價指數",          "美元/公噸"),
}


def fetch_alphavantage_energy() -> str:
    """
    從 Alpha Vantage 取得天然氣、Brent 原油、煤礦月均價（最近 3 個月）
    使用 demo key 時僅部分指標可用
    """
    lines = [
        "📉 【Alpha Vantage 能源月均價（最近 3 個月）】",
        "─" * 44,
    ]

    for func, (name, unit) in AV_COMMODITIES.items():
        url = (
            f"https://www.alphavantage.co/query"
            f"?function={func}&interval=monthly&apikey={AV_API_KEY}"
        )
        try:
            resp = requests.get(url, timeout=TIMEOUT)
            d = resp.json()

            # demo key 對部分 function 會回傳 Information 提示
            if "Information" in d:
                lines.append(f"  {name}：需申請正式 API Key")
                continue

            data = d.get("data", [])
            if not data:
                lines.append(f"  {name}：無資料")
                continue

            recent = data[:3]
            row = "  ".join(
                f"{e['date'][:7]}:{float(e['value']):.2f}" for e in recent
            )
            lines.append(f"  {name}")
            lines.append(f"    {row}  ({unit})")

        except Exception as e:
            lines.append(f"  {name}：抓取失敗（{e}）")

    lines.append("")
    lines.append("  * 如需 COAL 完整資料，請至 alphavantage.co 申請免費 key")
    lines.append("    申請後將 ALPHA_VANTAGE_KEY=YOUR_KEY 加入 .env 即可啟用")
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════
# 組合報告 & Telegram 推播
# ════════════════════════════════════════════════════════════

def build_report() -> str:
    """依序抓取各來源，組合成完整報告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("📡 正在抓取 IMF CPI 資料（台灣、美國及全球主要國家）...")
    imf_section = fetch_imf_cpi()

    print("📡 正在抓取 World Bank CPI 指數...")
    wb_section  = fetch_worldbank_cpi()

    print("📡 正在抓取國際能源價格（yfinance）...")
    energy_section = fetch_energy_prices()

    print("📡 正在抓取 Alpha Vantage 能源月均價...")
    av_section = fetch_alphavantage_energy()

    divider = "\n" + "━" * 28 + "\n"

    return (
        f"📈 【全球大宗商品與 CPI 報告】\n"
        f"🕐 更新時間：{now}\n"
        f"{'━' * 28}\n\n"
        + imf_section
        + divider
        + wb_section
        + divider
        + energy_section
        + divider
        + av_section
        + f"\n{'━' * 28}\n"
        "📡 資料來源：IMF / World Bank / Yahoo Finance / Alpha Vantage"
    )


async def send_text(bot: Bot, chat_id, text: str) -> None:
    """發送純文字，超過 4096 字自動分段"""
    if len(text) <= 4096:
        await bot.send_message(chat_id=chat_id, text=text)
    else:
        chunks = [text[i:i + 4096] for i in range(0, len(text), 4096)]
        for idx, chunk in enumerate(chunks, 1):
            await bot.send_message(chat_id=chat_id, text=chunk)
            print(f"   ✉️  第 {idx}/{len(chunks)} 段已送出")


async def broadcast(message: str) -> None:
    """推播至所有目標"""
    bot     = Bot(token=TELEGRAM_TOKEN)
    targets = [TARGET_USER_ID, TARGET_GROUP_ID, TARGET_CHANNEL]

    for chat_id in targets:
        print(f"\n📤 推播至目標：{chat_id}")
        try:
            await send_text(bot, chat_id, message)
            print(f"✅ 推播成功：{chat_id}")
        except Exception as e:
            print(f"❌ 推播至 {chat_id} 失敗：{e}")


async def main() -> None:
    report = build_report()

    print("\n" + "=" * 56)
    print(report)
    print("=" * 56 + "\n")

    await broadcast(report)
    print("\n🎉 所有推播任務完成！")


if __name__ == "__main__":
    asyncio.run(main())
