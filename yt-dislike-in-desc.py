import time
from datetime import datetime, timezone
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

interval = 3600 # in seconds

do_title = False 
do_description = True
do_unlisted = False

#VideoID = "dQw4w9WgXcQ" # rickroll
VideoID = "xoKtH5nE-dY" # Demo video

credentials = None

print ("Waiting for authentication. A browser window should open...")
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",
    scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
)
flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")
credentials = flow.credentials
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def get_video_info(id):
    return youtube.videos().list(
        id=id,
        part='snippet,statistics,status'
        ).execute()

def updatetitle(id, snippet, statistics):
    likeCount = statistics['likeCount']
    dislikeCount = statistics['dislikeCount']

    if (likeCount == "0" and dislikeCount == "0"):
        likeRatio = "0/0"
    else:
        likeRatio = str(round(100 * float(likeCount)/(float(likeCount)+float(dislikeCount)))) + "/100"

    dateString = str(datetime.now(timezone.utc))[:19]

    # for demo only
    if (do_title or id == VideoID):
        temp_title = "This video has " + dislikeCount + " dislikes."
        snippet['title'] = temp_title
    
    if(do_description):
        # Remove old dislikeCount.
        if (snippet['description'][:7] == "LIKES: "):
            snippet['description'] = snippet['description'].partition("\n")[2]

        # Create new string
        temp_desc = "LIKES: " + likeCount + "    DISLIKES: " + dislikeCount + "    Ratio: " + likeRatio + "    Last updated: " + dateString # + "update interval: " + str(interval) + " seconds."
        
        # Add dislikeCount.
        snippet['description'] = temp_desc + "\n" + snippet['description']

    youtube.videos().update(
    part='snippet',
    body=dict(
        id=id,
        snippet=snippet
    )).execute()

def main():
    # my channel uploads playlist
    playlistid = youtube.channels().list(mine='true', part='contentDetails').execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    while(True):
        print("updating...")

        playlist = youtube.playlistItems().list(playlistId=playlistid, part='contentDetails', maxResults='100').execute()['items']

        videoIds = []
        for video in playlist:
            videoIds.append(video['contentDetails']['videoId'])
        
        for id in videoIds:
            video = get_video_info(id)
            snippet = video['items'][0]['snippet']
            statistics = video['items'][0]['statistics']
            privacyStatus = video['items'][0]['status']['privacyStatus']
            if (privacyStatus == 'public' or (privacyStatus == 'unlisted' and do_unlisted)):
                updatetitle(id, snippet, statistics)
            
            elif (id == VideoID):
                updatetitle(id, snippet, statistics)
        time.sleep(interval)

main()
