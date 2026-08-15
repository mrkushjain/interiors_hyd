"""
Fetch all messages from the Sayuk Interiors Telegram group and save to JSON.
Run: uv run --with telethon python fetch_messages.py
"""
import asyncio
import json
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

API_ID = 31805135
API_HASH = "8d10e88dca431730b4ec33e4932d8daa"
PHONE = "+918630702850"
# Group link: https://web.telegram.org/a/#-1001659558760_24162
# Channel ID (without -100 prefix): 1659558760
CHANNEL_ID = -1001659558760

async def main():
    client = TelegramClient("sayuk_session", API_ID, API_HASH)
    await client.start(phone=PHONE)
    print("Logged in successfully.")

    messages = []
    count = 0
    async for msg in client.iter_messages(CHANNEL_ID, reverse=True):
        count += 1
        if count % 500 == 0:
            print(f"  Fetched {count} messages...")

        entry = {
            "id": msg.id,
            "date": msg.date.isoformat() if msg.date else None,
            "sender": None,
            "text": msg.text or "",
            "has_photo": isinstance(msg.media, MessageMediaPhoto),
            "has_document": isinstance(msg.media, MessageMediaDocument),
            "reply_to": msg.reply_to_msg_id,
        }

        # Try to get sender name
        if msg.sender:
            sender = msg.sender
            name_parts = []
            if hasattr(sender, "first_name") and sender.first_name:
                name_parts.append(sender.first_name)
            if hasattr(sender, "last_name") and sender.last_name:
                name_parts.append(sender.last_name)
            entry["sender"] = " ".join(name_parts) or getattr(sender, "username", None)

        messages.append(entry)

    print(f"Total messages fetched: {len(messages)}")

    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print("Saved to messages.json")
    await client.disconnect()

asyncio.run(main())
