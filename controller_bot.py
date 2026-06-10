import asyncio
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # ← Put your bot token

CONFIG_FILE = "adbot_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"ad_text": "", "groups": [], "running": False, "group_interval": 60, "batch_size": 5, "batch_interval": 300}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 **AdBot Controller**\n\n"
        "Commands:\n"
        "/setad <text>\n"
        "/addgroup <link>\n"
        "/groups\n"
        "/removegroup <link>\n"
        "/startads\n"
        "/stopads\n"
        "/status"
    )

async def set_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if text:
        config["ad_text"] = text
        save_config(config)
        await update.message.reply_text("✅ Ad text updated!")
    else:
        await update.message.reply_text("Usage: `/setad Your ad text`")

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/addgroup https://t.me/...`")
        return
    link = context.args[0]
    if link not in config["groups"]:
        config["groups"].append(link)
        save_config(config)
        await update.message.reply_text(f"✅ Added group: {link}")
    else:
        await update.message.reply_text("Already added.")

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config["groups"]:
        await update.message.reply_text("No groups added.")
        return
    text = "**Groups:**\n" + "\n".join(f"• {g}" for g in config["groups"])
    await update.message.reply_text(text)

async def remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/removegroup link`")
        return
    link = context.args[0]
    if link in config["groups"]:
        config["groups"].remove(link)
        save_config(config)
        await update.message.reply_text(f"✅ Removed: {link}")
    else:
        await update.message.reply_text("Not found.")

async def start_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config["running"] = True
    save_config(config)
    await update.message.reply_text("🚀 Ad posting **started**!")

async def stop_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config["running"] = False
    save_config(config)
    await update.message.reply_text("⛔ Ad posting **stopped**.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = "✅ Running" if config.get("running") else "⛔ Stopped"
    await update.message.reply_text(
        f"**AdBot Status**\n"
        f"Status: {status}\n"
        f"Groups: {len(config['groups'])}\n"
        f"Ad Text: {config['ad_text'][:100]}..."
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setad", set_ad))
    app.add_handler(CommandHandler("addgroup", add_group))
    app.add_handler(CommandHandler("groups", list_groups))
    app.add_handler(CommandHandler("removegroup", remove_group))
    app.add_handler(CommandHandler("startads", start_ads))
    app.add_handler(CommandHandler("stopads", stop_ads))
    app.add_handler(CommandHandler("status", status))

    print("🤖 Controller Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
