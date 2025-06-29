from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

from decouple import config

BOT_TOKEN = config("BOT_TOKEN")


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Пример: /analyze BTC/USDT")
        return

    symbol = args[0]
    timeframes = ["1h", "4h", "1d"]
    url = f"http://localhost:8000/analyze?symbol={symbol}"
    for tf in timeframes:
        url += f"&timeframes={tf}"

    try:
        res = requests.get(url)
        data = res.json()
        message = f"📊 Анализ {symbol}\n"
        for tf, info in data.items():
            message += (
                f"\n🕒 {tf}:\n"
                f"- {info['signal']}\n"
                f"- Entry: {info['entry_zone']}\n"
                f"- Price: {info['last_price']}\n"
                f"- Volume: {info.get('volume', 'n/a')}\n"
            )

            if info.get("fvg"):
                message += f"- FVG: {info['fvg']}\n"

            if info.get("breaker_block"):
                message += f"- Order Block: {info['breaker_block']}\n" # тут поменено бред

            if info.get("liquidity"):
                message += f"- Liquidity ↑: {info['liquidity']['above']}\n"
                message += f"- Liquidity ↓: {info['liquidity']['below']}\n"
            
            if info.get("funding_rate_%") is not None:
                message += f"- Funding Rate: {info['funding_rate_%']}%\n"


        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.run_polling()