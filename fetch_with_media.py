"""
Fetch interior-related messages WITH media (photos/videos) from the Sayuk Interiors group.
Also extracts all company mentions and groups them.

Run: uv run --with telethon python fetch_with_media.py
"""
import asyncio, json, os, re
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

API_ID = 31805135
API_HASH = "8d10e88dca431730b4ec33e4932d8daa"
PHONE = "+918630702850"
CHANNEL_ID = -1001659558760

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)

# All known interior companies / keywords to match messages
COMPANY_PATTERNS = {
    "SpaceV Interior Designs": ["spacev", "space v", "vasu", "8500010069"],
    "HomeLane": ["homelane", "home lane", "8179456656"],
    "SLV Interiors": ["slv interior", "9666886132"],
    "Interazzo": ["interazzo"],
    "Trendy Space Interior": ["trendy space", "kiran potu", "9948591230"],
    "Mohan (Independent)": ["8099192769", "mohan.*interior"],
    "Mega Interiors": ["mega interior", "9247611111"],
    "Casa Interiors And Decor": ["casa interior", "85999 47444", "8599947444"],
    "Iris Design Studio": ["iris design", "99495 12847", "9949512847"],
    "5 Tattva Design Studio": ["5 tattva", "tattva.*design", "9913957537"],
    "My Space Design Studio": ["my space design", "9515133080", "8125920636", "amarender"],
    "Houspace": ["houspace", "90000 83426", "9000083426"],
    "Luxus Design Studio": ["luxus", "9049713333", "97797 72579", "9779772579"],
    "Woodz & Nails Interiors": ["woodz.*nails", "woodz and nails"],
    "Care Interiors": ["care interior"],
    "Painter Manish": ["painter manish", "manish.*paint", "9515552622"],
    "Carpenter Gautam": ["carpenter gautam", "gautam.*carpentr", "9651202712"],
    "Nilesh Gaydhani": ["nilesh", "gaydhani", "9881472773"],
    "Icons Interiors": ["icons interior"],
    "Axiis Interiors": ["axiis"],
    "Dzine Studio": ["dzine studio"],
    "YesYou Interiors": ["yesyou", "yes you interior", "78912 42360"],
    "Salt Interiors": ["salt interior", "9573285458"],
    "Wurfel Interiors": ["wurfel", "8769836054"],
    "Nifty Interio": ["nifty interio", "99666 60069"],
    "Livspace": ["livspace", "liv space"],
    "Homelane": ["homelane"],
    "Arista": ["arista interior"],
    "Design Cafe": ["design cafe"],
    "Dlife": ["dlife"],
    "Chicspaces": ["chicspaces"],
    "Casa Rico": ["casa rico"],
    "Tint Tone and Shade": ["tint tone", "tint.*shade"],
}

def match_companies(text):
    matched = []
    tl = text.lower()
    for company, patterns in COMPANY_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, tl):
                matched.append(company)
                break
    return matched

async def main():
    client = TelegramClient("sayuk_session", API_ID, API_HASH)
    await client.start(phone=PHONE)
    print("Logged in.")

    # Load existing messages
    with open("messages.json") as f:
        all_msgs = json.load(f)

    # Build id->msg map
    msg_map = {m["id"]: m for m in all_msgs}

    # Find interior-related message IDs
    interior_kw = ["interior", "design", "modular", "false ceiling", "flooring",
                   "woodwork", "furniture", "painting", "carpenter", "wallpaper",
                   "wardrobe", "kitchen", "decor", "furnish", "civil work"]

    interior_ids = set()
    for m in all_msgs:
        t = m["text"].lower()
        if any(k in t for k in interior_kw) and len(m["text"]) > 20:
            interior_ids.add(m["id"])
        # Also include any message matching a company pattern
        if match_companies(m["text"]):
            interior_ids.add(m["id"])

    print(f"Interior-related messages to process: {len(interior_ids)}")

    # Download media for interior messages that have photos/videos
    media_msgs = [m for m in all_msgs if m["id"] in interior_ids and (m["has_photo"] or m["has_document"])]
    print(f"Messages with media to download: {len(media_msgs)}")

    media_map = {}  # msg_id -> [filename, ...]

    downloaded = 0
    skipped = 0
    for i, m in enumerate(media_msgs):
        msg_id = m["id"]
        # Check if already downloaded
        existing = list(MEDIA_DIR.glob(f"{msg_id}_*"))
        if existing:
            media_map[msg_id] = [str(f.name) for f in existing]
            skipped += 1
            continue

        try:
            tg_msg = await client.get_messages(CHANNEL_ID, ids=msg_id)
            if tg_msg and tg_msg.media:
                if isinstance(tg_msg.media, MessageMediaPhoto):
                    ext = "jpg"
                elif isinstance(tg_msg.media, MessageMediaDocument):
                    mime = getattr(tg_msg.media.document, "mime_type", "")
                    if "video" in mime:
                        ext = "mp4"
                    elif "image" in mime:
                        ext = "jpg"
                    else:
                        ext = "bin"
                    # Skip large videos > 50MB
                    size = getattr(tg_msg.media.document, "size", 0)
                    if size > 50 * 1024 * 1024:
                        print(f"  Skipping large file {msg_id} ({size//1024//1024}MB)")
                        continue
                else:
                    continue

                fname = f"{msg_id}_{i}.{ext}"
                fpath = MEDIA_DIR / fname
                await client.download_media(tg_msg, str(fpath))
                media_map[msg_id] = media_map.get(msg_id, []) + [fname]
                downloaded += 1
                if downloaded % 20 == 0:
                    print(f"  Downloaded {downloaded} media files...")
        except Exception as e:
            print(f"  Error on msg {msg_id}: {e}")
            continue

    print(f"Media: {downloaded} downloaded, {skipped} already cached")

    # Now group all messages by company
    company_data = {name: {"messages": [], "phones": set(), "urls": set()} for name in COMPANY_PATTERNS}

    phone_re = re.compile(r'(?:\+91[\s\-]?)?[6-9]\d{9}|(?:\+91[\s\-]?)?\d{5}[\s]\d{5}|\d{5}\s\d{5}')
    url_re = re.compile(r'https?://\S+')

    for m in all_msgs:
        if not m["text"] and not m["has_photo"]:
            continue
        companies = match_companies(m["text"])
        if not companies:
            continue

        phones = phone_re.findall(m["text"])
        urls = [u.rstrip(".,)") for u in url_re.findall(m["text"])]
        media_files = media_map.get(m["id"], [])

        entry = {
            "id": m["id"],
            "date": m["date"][:10] if m["date"] else "",
            "sender": m["sender"] or "Unknown",
            "text": m["text"],
            "phones": phones,
            "urls": urls,
            "media": media_files,
            "has_photo": m["has_photo"],
        }

        for company in companies:
            if company in company_data:
                company_data[company]["messages"].append(entry)
                company_data[company]["phones"].update(phones)
                company_data[company]["urls"].update(urls)

    # Convert sets to lists
    for name in company_data:
        company_data[name]["phones"] = list(company_data[name]["phones"])
        company_data[name]["urls"] = list(company_data[name]["urls"])
        # Sort messages by date
        company_data[name]["messages"].sort(key=lambda x: x["date"])

    # Filter to companies with at least 1 message
    company_data = {k: v for k, v in company_data.items() if v["messages"]}

    with open("company_data.json", "w") as f:
        json.dump(company_data, f, ensure_ascii=False, indent=2)

    print(f"\nCompanies with mentions: {len(company_data)}")
    for name, data in sorted(company_data.items(), key=lambda x: -len(x[1]["messages"])):
        media_count = sum(len(e["media"]) for e in data["messages"])
        print(f"  {name}: {len(data['messages'])} mentions, {media_count} media files")

    await client.disconnect()
    print("\nDone! Run build_dashboard2.py to generate the dashboard.")

asyncio.run(main())
