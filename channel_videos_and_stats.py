from googleapiclient.discovery import build
import pandas as pd

api_key= "< Paste the Google API Key here >"
youtube = build("youtube","v3", developerKey=api_key)

## Copy the URL of any Yotube video paste it in the "url" variable to get the stats of the channel that published the video.
url="< Paste the URL of a Youtube video >"
nextPageToken = None

# Name of the dictionary
videos=[]

## Splitting the channel_id from the video URL that was provided on the "url" variable.
single_video_id = url.split("=")[1].split("&")[0]

# part is a required parameter to make this method work. 
# Inside this parameter you can specify the resources you want the API to return. In this case we want to return "snippet" 
# Fore more information check the documentation that I shared for the list() method.
channel_id= youtube.videos().list(part="snippet",id=single_video_id).execute()["items"][0]["snippet"]["channelId"]

# Key Stats of the Channel
# Part is a required parameter to make this method work.
# Fore more information check the documentation that I shared for the list() method.
channel_stats = youtube.channels().list(
    part=["statistics","snippet"],
    id=channel_id
    ).execute()

# Get the "ID" of the "Upload" playlist. 
upload = str(youtube.channels().list(

    # Part is a required parameter to make this method work. 
    # Inside this parameter you can specify the resources you want the API to return. 
    # Fore more information check the documentation that I shared for the list() method. 
    part="contentDetails",
    id= channel_id
    ).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])

playlist_id = upload

while True:

    # Request the first 50 videos of a channel. This is the full dictionary. The result is store in a variable called "pl_response".
    # PageToken at this point is "None"
    pl_request= youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=50,
        pageToken= nextPageToken
    )

    # Store in a list the first 50 videoId's from the dictionary that we stored on "pl_response"
    pl_response = pl_request.execute()
    
    vid_ids=[]
    
    for item in pl_response["items"]:
        vid_ids.append(item["contentDetails"]["videoId"])

    # You get the stats of the first 50 videos.
    vid_request = youtube.videos().list(
        part=["snippet","statistics"],
        id=",".join(vid_ids)
    )

    vid_response = vid_request.execute()
    
    # Send the amount of views and the URL of each video to the videos empty list that was declared at the beginning of the code.
    for i in vid_response["items"]:
        vid_views = i["statistics"]
        vid_snip = i["snippet"]
        vid_thumb = i["snippet"]["thumbnails"]["medium"]

        vid_id = i["id"]
        yt_lin = f"https://youtu.be/{vid_id}"

        videos.append( 
            {
                "published":vid_snip.get("publishedAt","0"),
                "title":vid_snip.get("title","0"),
                "views":int(vid_views.get("viewCount","0")),
                "likes":int(vid_views.get("likeCount","0")),
                "dislikes":int(vid_views.get("dislikeCount","0")),
                "comments":int(vid_views.get("commentCount","0")),
                "description":vid_snip.get("description","0"),
                "thumbnails":vid_thumb.get("url","0"),
                "url" :yt_lin
            }
        )

    nextPageToken = pl_response.get("nextPageToken")

    if not nextPageToken:
        break

# Export to a CSV file the dictionary with all the key stats of all the videos from a Youtube channel
name_of_file= f"{title_of_channel}.csv".replace(" ","_")
pd.DataFrame.from_dict(videos).to_csv(name_of_file)