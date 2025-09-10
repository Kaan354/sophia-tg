import os
from fastapi import FastAPI, HTTPException
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

SESSION_NAME = "session"

app = FastAPI()

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@app.on_event("startup")
async def startup():
    await client.connect()
    if not await client.is_user_authorized():
        sent = await client.send_code_request(PHONE_NUMBER)
        app.state.phone_code_hash = sent.phone_code_hash
        print("👉 Code sent. Now call /verify with your Telegram code.")

@app.on_event("shutdown")
async def shutdown():
    await client.disconnect()

@app.post("/verify")
async def verify(payload: dict):
    code = payload.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    phone_code_hash = getattr(app.state, "phone_code_hash", None)
    if not phone_code_hash:
        raise HTTPException(status_code=400, detail="No phone_code_hash stored. Restart server to request a new code.")

    try:
        await client.sign_in(PHONE_NUMBER, code, phone_code_hash=phone_code_hash)
        return {"status": "ok", "message": "Logged in successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"status": "running"}
