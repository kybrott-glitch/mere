import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest

API_ID = 38190726                    # ← Your API ID
API_HASH = '66a4eebff562f2035bf2acabec3dd7d5'      # ← Your API Hash

CONFIG_FILE = "adbot_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "ad_text": "🔥 Default ad text here",
        "groups": [],
        "group_interval": 60,
        "batch_size": 5,
        "batch_interval": 300,
        "running": False
    }

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()
client = None
posting_task = None

async def get_client():
    global client
    if client is None:
        client = TelegramClient("ad_session", API_ID, API_HASH)
        await client.start()
    return client

async def posting_loop():
    cl = await get_client()
    while config.get("running", False):
        for i in range(0, len(config["groups"]), config["batch_size"]):
            if not config.get("running"):
                break
            batch = config["groups"][i:i + config["batch_size"]]

            for group in batch:
                if not config.get("running"):
                    break
                try:
                    entity = await cl.get_entity(group)
                    try:
                        await cl(JoinChannelRequest(entity))
                    except UserAlreadyParticipantError:
                        pass

                    await cl.send_message(entity, config["ad_text"], parse_mode='html')
                    print(f"📤 Posted → {group}")
                    await asyncio.sleep(config["group_interval"])
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 30)
                except Exception as e:
                    print(f"Error {group}: {e}")
                    await asyncio.sleep(10)

            await asyncio.sleep(config["batch_interval"])
        await asyncio.sleep(30)

async def main():
    cl = await get_client()
    print("✅ Ad Userbot is running in background...")

    # Auto-start if it was running before
    if config.get("running"):
        global posting_task
        posting_task = asyncio.create_task(posting_loop())

    await cl.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
