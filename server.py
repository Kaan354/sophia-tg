import os
from fastapi import FastAPI
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PHONE_CODE = os.getenv("PHONE_CODE")   # temporary, will change per login attempt
PASSWORD = os.getenv("PASSWORD")       # if you have 2FA

SESSION = "my_session"

app = FastAPI()
client = TelegramClient(SESSION, API_ID, API_HASH)

@app.on_event("startup")
async def startup():
    await client.connect()
    if not await client.is_user_authorized():
        try:
            if PHONE_CODE:  # login with code
                await client.sign_in(PHONE_NUMBER, PHONE_CODE)
            else:  # request code first
                await client.send_code_request(PHONE_NUMBER)
                print("⚠️ Please set PHONE_CODE env var with the received code and redeploy.")
        except Exception as e:
            if "password" in str(e).lower() and PASSWORD:
                await client.sign_in(password=PASSWORD)
            else:
                raise

@app.get("/")
async def root():
    me = await client.get_me()
    return {"status": "running", "user": me.username if me else None}
