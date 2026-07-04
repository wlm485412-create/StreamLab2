import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload  # থাম্বনেইল আপলোডের লাইব্রেরি

# আপনার সেট করে দেওয়া ইনফরমেশন
TITLE = "Daily Mind Game Challenge | LIVE Puzzle Challenge"

DESCRIPTION = """Welcome to the Daily Live Puzzle Challenge! 🧠⚡

Test your brain power with exciting puzzles and mind games — and remember, you only get 60 seconds to solve each one!

🔥 Play along in real time  
⏱️ One minute per puzzle  
🏆 Challenge your IQ  
💬 Compete with other viewers in the chat  

Whether you love riddles, brain teasers, logic puzzles, or tricky challenges, this live stream is designed to sharpen your mind and boost your thinking speed.

👉 Don’t forget to LIKE 👍  
👉 SUBSCRIBE for daily puzzle lives  
👉 Turn on the notification bell 🔔 so you never miss a challenge!

Are you ready to prove you're a puzzle master? Let’s begin!"""

TAGS = ["live puzzle","puzzle live","brain teaser live","iq test live","mind games live","puzzle challenge","brain challenge","riddles live","logic puzzles","test your iq","genius puzzle","daily puzzle","interactive live","youtube live games","thinking games","smart games","brain workout","puzzle stream","live brain teaser","60 second challenge","quick puzzles","viral puzzles","fun puzzles"]

def main():
    print("🚀 Initializing Vertical API Stream...")
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

    creds = Credentials(None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    youtube = build("youtube", "v3", credentials=creds)

    # ১. ব্রডকাস্ট তৈরি করা
    broadcast_body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "scheduledStartTime": (datetime.datetime.utcnow() + datetime.timedelta(seconds=60)).isoformat() + "Z"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        },
        "contentDetails": {
            "enableAutoStart": True,
            "enableAutoStop": True,
            "monitorStream": { "enableMonitorStream": False } 
        }
    }
    
    broadcast_resp = youtube.liveBroadcasts().insert(part="snippet,status,contentDetails", body=broadcast_body).execute()
    broadcast_id = broadcast_resp["id"]
    print(f"✅ Broadcast Created! ID: {broadcast_id}")

    # ১.৫. থাম্বনেইল আপলোড (নতুন যুক্ত অংশ) 📸
    thumbnail_file = "thumbnail.jpg"
    if os.path.exists(thumbnail_file):
        print("Uploading Thumbnail...")
        try:
            youtube.thumbnails().set(
                videoId=broadcast_id,
                media_body=MediaFileUpload(thumbnail_file)
            ).execute()
            print("✅ Thumbnail Added Successfully!")
        except Exception as e:
            print(f"❌ Failed to add Thumbnail. Error: {e}")
    else:
        print("⚠️ 'thumbnail.jpg' file not found in the repository! Proceeding without thumbnail.")

    # ২. স্ট্রিম কি জেনারেট (Variable)
    stream_insert = youtube.liveStreams().insert(
        part="snippet,cdn",
        body={
            "snippet": { "title": "Vertical 1080x1920 Auto Stream" },
            "cdn": {
                "ingestionType": "rtmp",
                "resolution": "variable",
                "frameRate": "variable"
            }
        }
    ).execute()
    
    stream_id = stream_insert["id"]
    ingestion = stream_insert["cdn"]["ingestionInfo"]
    rtmp_url = ingestion["ingestionAddress"]
    stream_key = ingestion["streamName"]
    
    # ৩. বাইন্ড (ব্রডকাস্ট ও কী যুক্ত করা)
    youtube.liveBroadcasts().bind(part="id,contentDetails", id=broadcast_id, streamId=stream_id).execute()
    print("✅ Bind Successful!")

    # ৪. গিটহাব আউটপুট
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        print(f"server_url={rtmp_url}", file=f)
        print(f"stream_key={stream_key}", file=f)

if __name__ == "__main__":
    main()