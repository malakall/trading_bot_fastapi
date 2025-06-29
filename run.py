import multiprocessing
import uvicorn
from app.telegram_bot.bot import run_bot

def start_api():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

def start_bot():
    run_bot()

if __name__ == "__main__":
    multiprocessing.Process(target=start_api).start()
    multiprocessing.Process(target=start_bot).start()
