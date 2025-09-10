from fastapi import FastAPI
from telethon import TelegramClient

API_ID = 22348068       # get this from https://my.telegram.org/apps
API_HASH = "7e531486fa7e8eb45f57d1a0fa302d8a"
SESSION = "sophia_telegram_session"

app = FastAPI()
client = TelegramClient(SESSION, API_ID, API_HASH)

@app.on_event("startup")
async def startup():
    await client.start()  # will ask for phone & code on first run (in Render logs)
    print("✅ Telethon client started")

@app.on_event("shutdown")
async def shutdown():
    await client.disconnect()

@app.post("/send_message/")
async def send_message(chat_id: str, text: str):
    await client.send_message(chat_id, text)
    return {"status": "ok", "chat_id": chat_id, "message": text}
