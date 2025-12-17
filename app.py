import json
import time
import os
from pyrogram import Client
from pyrogram.errors import FloodWait
import requests

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
GROUP_ID = int(os.environ["GROUP_ID"])
SESSION_STRING = os.environ["SESSION_STRING"]
DELAY = int(os.environ.get("DELAY", 60))

# Heroku Config Vars API
HEROKU_APP_NAME = os.environ["HEROKU_APP_NAME"]
HEROKU_API_KEY = os.environ["HEROKU_API_KEY"]

SONG_FILE = "old_hindi_top_1000.json"
INDEX_KEY = "LAST_INDEX"


def get_last_index():
    return int(os.environ.get(INDEX_KEY, 0))


def save_last_index(index):
    url = f"https://api.heroku.com/apps/{HEROKU_APP_NAME}/config-vars"
    headers = {
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3",
        "Content-Type": "application/json"
    }
    requests.patch(url, headers=headers, json={INDEX_KEY: str(index)})


def run():
    app = Client(
        ":memory:",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )

    with open(SONG_FILE, "r", encoding="utf-8") as f:
        songs = json.load(f)

    start = get_last_index()
    print("Resuming from index:", start)

    with app:
        for i in range(start, len(songs)):
            title = songs[i]["title"].strip()
            try:
                app.send_message(GROUP_ID, f"/play {title}")
                print(f"Sent {i+1}: {title}")

                save_last_index(i + 1)
                time.sleep(DELAY)

            except FloodWait as e:
                time.sleep(e.value)

            except Exception as e:
                print("Error:", e)
                break


while True:
    try:
        run()
    except Exception as e:
        print("Restarting:", e)
        time.sleep(60)
