# Key stats of every video published by a Youtube channel.
This script is part of my research project called "What Topics Drives Youtube MX?". You can check the whole project [**here**](https://gmarr.com/).

The main purpose of this code is to get the most relevant statistics from all the youtube videos of a single channel and export them into a CSV. 

Here's an example of the final result you can get after running the script:

published | title | views | likes | dislikes | comments | description | thumbnails | url
---|---|---|---|---|---|---|---|---
2017-01-19 21:42:24+00:00|How a $300,000 Speaker is Made|3697049|37592|8585|5578|Oswalds Mill Audio makes $300,000 speakers fro...|https://i.ytimg.com/vi/wX65iSZTI7E/mqdefault.jpg|https://youtu.be/wX65iSZTI7E
2019-01-24 20:57:42+00:00|Inside China's High-Tech Dystopia|3058129|45312|8171|7242|In part three of Hello World Shenzhen, Bloombe...|https://i.ytimg.com/vi/ydPqKhgh9Mg/mqdefault.jpg|https://youtu.be/ydPqKhgh9Mg

## **Tutorial**
---
### <ins>**1. General Concepts**</ins>
To follow the code in this tutorial I would recommend to have some knowledge of the next concepts:
* Python
    * `for` loops
    * functions
    * pip. 
        * [Here](https://realpython.com/what-is-pip/) you can find a really good article that expalins what is pip.
    * pandas. 
        * [This](https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html) is a gentle introduction to the pandas library.
* JSON
    * The general structure of a JSON file
* API's
    * Specifically, the tutorial is going to make more sense if you know what is an API Key. To learn more about API's I recommend to watch this [video](https://www.youtube.com/watch?v=GZvSYJDk-us&t=4641s). The video shows the inner workings of the [Trello API](https://developer.atlassian.com/cloud/trello/rest/) however, the concepts that are shown can be applied to any API. This is my "go-to" reference guide when I'm stucked.

If you do not know how any of this concepts work I added resources troughout the tutorial so you can revised them at your own pace.

### <ins>**2. The Set Up**</ins>
In addition to the concepts mentioned above, before you start the tutorial be sure to have:

* A Youtube API Key
    * In order to retrieve the data from Youtube we're going to use the [Youtube API](https://developers.google.com/youtube/v3). All the API's from Google properties require a Google Account and autorization credentials.
    * To learn how to setup a Google Account and get this credentials you can follow this [tutorial](https://developers.google.com/youtube/registering_an_application).
    * Once you have your credentials, you need to request an API Key. You can follow [this instructions](https://cloud.google.com/resource-manager/docs/creating-managing-projects?visit_id=637472330160631271-1024614839&rd=1) to get your API Key.
    * If you want additional information about the API setup, Youtube offers a nice introduction [here](https://developers.google.com/youtube/v3/getting-started).
* A Code Editor
    * I use VS Code. You can download it [here](https://code.visualstudio.com/).
* Python
    * If you use a Mac you already have Python installed. If you use a Windows PC or Linux, you can download Python [here]("").
    * The `pandas` library. You can download it from [here](https://pandas.pydata.org/).

### <ins>**3. The Code**</ins>

1. The first building block you need for this project can be found [**here**](https://github.com/germarr/yotube_channel_stats/blob/main/README.md). Be sure to check the tutorial on that link before continuing the tutorial.

2. After checking the code from point **1**  the code should look like this:
```python
from googleapiclient.discovery import build

api_key= "< Paste the Google API Key here >"

youtube = build("youtube","v3", developerKey=api_key)

url="< Paste the URL of a Youtube video >"

single_video_id = url.split("=")[1].split("&")[0]
channel_id= youtube.videos().list(part="snippet",id=single_video_id).execute()["items"][0]["snippet"]["channelId"]

channel_stats = youtube.channels().list(
    part=["statistics","snippet"],
    id=channel_id
    ).execute()
```
3. Upload Code

```python
#Get the "ID" of the "Upload" playlist. 
upload = str(youtube.channels().list( 
    # Part is a required parameter to make this method work. 
    # Inside this parameter you can specify the resources you want the API to return. 
    # Fore more information check the documentation that I shared for the list() method.
    part="contentDetails",
    id= channel_id
    ).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])
```
4. Loop Code to get all the videos

```python
# Basic Setup
nextPageToken = None
playlist_id = upload

# Name of the dictionary
videos=[]

while True:
    # Request the first 50 videos of a channel. This is the full dictionary. The result is store in a variable called "pl_response".
    # PageToken at this point is "None"
    pl_request= youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=50,
        pageToken= nextPageToken
    )

    pl_response = pl_request.execute()
    
    # Store in a list the first 50 videoId's from the dictionary that we stored on "pl_response"
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

videos.sort(key=lambda vid: vid["comments"], reverse =False)
```
5. Naming the file

```python
name_of_file= f"{title_of_channel}.csv".replace(" ","_")
```
6. Turn the dictionary into a pandas dataframe and into a CSV file.
```python
import pandas as pd

pd.DataFrame.from_dict(videos).to_csv(name_of_file)
```
7. All code
```python
from googleapiclient.discovery import build
import pandas as pd

api_key= "< Paste the Google API Key here >"
youtube = build("youtube","v3", developerKey=api_key)
url="< Paste the URL of a Youtube video >"
nextPageToken = None
videos=[]

single_video_id = url.split("=")[1].split("&")[0]
channel_id= youtube.videos().list(part="snippet",id=single_video_id).execute()["items"][0]["snippet"]["channelId"]

channel_stats = youtube.channels().list(
    part=["statistics","snippet"],
    id=channel_id
    ).execute()
    
upload = str(youtube.channels().list( 
    part="contentDetails",
    id= channel_id
    ).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])

playlist_id = upload

while True:
    pl_request= youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=50,
        pageToken= nextPageToken
    )

    pl_response = pl_request.execute()
    vid_ids=[]
    
    for item in pl_response["items"]:
        vid_ids.append(item["contentDetails"]["videoId"])
    
    vid_request = youtube.videos().list(
        part=["snippet","statistics"],
        id=",".join(vid_ids)
    )

    vid_response = vid_request.execute()

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

name_of_file= f"{title_of_channel}.csv".replace(" ","_")
pd.DataFrame.from_dict(videos).to_csv(name_of_file)
```

