import json
import time
import os
from pyrogram import Client
from pyrogram.errors import FloodWait

API_ID = int(os.environ.get("API_ID", 28294093))
API_HASH = os.environ.get("API_HASH", "f24d982c45ab2f69a6cb8c0fee9630bd")
GROUP_ID = int(os.environ.get("GROUP_ID", -1003688195759))
DELAY = int(os.environ.get("DELAY", 60))

# SESSION handling
SESSION_STRING = os.environ.get("SESSION_STRING")   # Heroku
SESSION_NAME = os.environ.get("SESSION_NAME", "music_user")  # VPS

SONG_FILE = "old_hindi_top_1000.json"
PROGRESS_FILE = "progress.json"
# =========================================


def load_index():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return int(json.load(f).get("index", 0))
        except Exception:
            return 0
    return 0


def save_index(next_index):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"index": next_index}, f)


def get_client():
    if SESSION_STRING:
        return Client(
            ":memory:",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION_STRING
        )
    else:
        return Client(
            SESSION_NAME,
            api_id=API_ID,
            api_hash=API_HASH
        )


def run_once():
    app = get_client()

    with open(SONG_FILE, "r", encoding="utf-8") as f:
        songs = json.load(f)

    start_index = load_index()
    print("Resuming from index:", start_index)

    with app:
        # Force peer resolve once (prevents peer id invalid)
        app.get_chat(GROUP_ID)

        for i in range(start_index, len(songs)):
            title = songs[i]["title"].strip()

            try:
                app.send_message(GROUP_ID, f"/play {title}")
                print(f"Sent {i + 1}/{len(songs)}: {title}")

                # 🔑 CRITICAL FIX: save NEXT index
                save_index(i + 1)

                time.sleep(DELAY)

            except FloodWait as e:
                print("FloodWait:", e.value)
                time.sleep(e.value)

            except Exception as e:
                print("Error while sending:", e)
                time.sleep(20)
                return   # 🔥 return, NOT break


# ===== CRASH-SAFE LOOP =====
while True:
    try:
        run_once()
        print("All songs sent. Exiting.")
        break
    except Exception as e:
        print("CRASHED. Restarting in 60s:", e)
        time.sleep(60)
