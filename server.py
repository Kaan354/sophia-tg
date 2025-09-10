import os
from fastapi import FastAPI
from telethon import TelegramClient

# Environment variables from Render dashboard
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PHONE_CODE = os.getenv("PHONE_CODE")           # Only set this after you get the SMS
PHONE_CODE_HASH = os.getenv("PHONE_CODE_HASH") # Set this after first deploy
PASSWORD = os.getenv("PASSWORD")               # Optional, only if your account has 2FA

# Session file will persist on Render's disk (ephemeral between deploys, but ok if you don’t restart too often)
SESSION = "my_session"

app = FastAPI()
client = TelegramClient(SESSION, API_ID, API_HASH)


@app.on_event("startup")
async def startup():
    await client.connect()
    if not await client.is_user_authorized():
        if not PHONE_CODE:
            # Step 1: ask Telegram to send a code
            result = await client.send_code_request(PHONE_NUMBER)
            print("⚠️ Add this to Render Env Vars PHONE_CODE_HASH =", result.phone_code_hash)
        else:
            # Step 2: use the code and hash to log in
            await client.sign_in(
                phone=PHONE_NUMBER,
                code=PHONE_CODE,
                phone_code_hash=PHONE_CODE_HASH
            )
            if PASSWORD:
                await client.sign_in(password=PASSWORD)


@app.get("/")
async def root():
    """Check if the client is logged in."""
    me = await client.get_me()
    return {
        "status": "running",
        "logged_in_as": me.username if me else None
    }
