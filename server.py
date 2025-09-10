import os
from fastapi import FastAPI
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PHONE_CODE = os.getenv("PHONE_CODE")   # the code you receive
PHONE_CODE_HASH = os.getenv("PHONE_CODE_HASH")  # store this after first step
PASSWORD = os.getenv("PASSWORD")       # optional (2FA)

SESSION = "my_session"

app = FastAPI()
client = TelegramClient(SESSION, API_ID, API_HASH)

@app.on_event("startup")
async def startup():
    await client.connect()
    if not await client.is_user_authorized():
        if not PHONE_CODE:  # step 1: request code
            result = await client.send_code_request(PHONE_NUMBER)
            print("⚠️ Set PHONE_CODE_HASH env var to:", result.phone_code_hash)
        else:  # step 2: confirm with code + hash
            await client.sign_in(PHONE_NUMBER, PHONE_CODE, PHONE_CODE_HASH)
            if PASSWORD:  # if 2FA
                await client.sign_in(password=PASSWORD)

@app.get("/")
async def root():
    me = await client.get_me()
    return {"status": "running", "user": me.username if me else None}
