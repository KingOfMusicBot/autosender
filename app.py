import json
import time
import os
from pyrogram import Client
from pyrogram.errors import FloodWait

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
GROUP_ID = int(os.environ["GROUP_ID"])
SESSION_STRING = os.environ["SESSION_STRING"]
DELAY = int(os.environ.get("DELAY", 60))

SONG_FILE = "old_hindi_top_1000.json"
PROGRESS_FILE = "progress.json"   # TEMP (dyno life)

def load_index():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f).get("index", 0)
    return 0

def save_index(i):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"index": i}, f)

app = Client(
    ":memory:",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

with open(SONG_FILE, "r", encoding="utf-8") as f:
    songs = json.load(f)

start = load_index()
print("Resuming from index:", start)

with app:
    # IMPORTANT: force peer resolution once
    app.get_chat(GROUP_ID)

    for i in range(start, len(songs)):
        title = songs[i]["title"].strip()

        try:
            app.send_message(GROUP_ID, f"/play {title}")
            print(f"Sent {i+1}: {title}")

            save_index(i + 1)
            time.sleep(DELAY)

        except FloodWait as e:
            time.sleep(e.value)

        except Exception as e:
            print("Error:", e)
            time.sleep(20)
