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

SONG_FILE = "songs.json"
PROGRESS_FILE = "progress.json"


def load_index():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f).get("index", 0)
    return 0


def save_index(i):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"index": i}, f)


def get_client():
    if SESSION_STRING:
        # Heroku (no session file)
        return Client(
            ":memory:",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION_STRING
        )
    else:
        # VPS (session file)
        return Client(
            SESSION_NAME,
            api_id=API_ID,
            api_hash=API_HASH
        )


def run():
    app = get_client()

    with open(SONG_FILE, "r", encoding="utf-8") as f:
        songs = json.load(f)

    start = load_index()
    print("Resuming from index:", start)

    with app:
        # Force peer resolve once (fix peer id invalid)
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
                break


while True:
    try:
        run()
    except Exception as e:
        print("CRASHED, restarting in 60s:", e)
        time.sleep(60)
