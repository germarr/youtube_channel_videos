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
To follow the code in this tutorial I would recommend having some knowledge of the next concepts:
* Python
    * `for` loops
    * functions
    * pip. 
        * [Here](https://realpython.com/what-is-pip/) you can find a really good article that explains what is pip.
    * pandas. 
        * [This](https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html) is a gentle introduction to the pandas library.
* JSON
    * The general structure of a JSON file
* API's
    * Specifically, the tutorial is going to make more sense if you know what is an API Key. To learn more about API's I recommend watching this [video](https://www.youtube.com/watch?v=GZvSYJDk-us&t=4641s). The video shows the inner workings of the [Trello API](https://developer.atlassian.com/cloud/trello/rest/) however, the concepts that are shown can be applied to any API. This is my "go-to" reference guide when I'm stuck.

If you do not know how any of these concepts work I added resources throughout the tutorial so you can revise them at your own pace.

### <ins>**2. The Set Up**</ins>
In addition to the concepts mentioned above, before you start the tutorial be sure to have:

* A Youtube API Key
    * In order to retrieve the data from Youtube we're going to use the [Youtube API](https://developers.google.com/youtube/v3). All the APIs from Google properties require a Google Account and authorization credentials.
    * To learn how to set up a Google Account and get these credentials you can follow this [tutorial](https://developers.google.com/youtube/registering_an_application).
    * Once you have your credentials, you need to request an API Key. You can follow [this instruction](https://cloud.google.com/resource-manager/docs/creating-managing-projects?visit_id=637472330160631271-1024614839&rd=1) to get your API Key.
    * If you want additional information about the API setup, Youtube offers a nice introduction [here](https://developers.google.com/youtube/v3/getting-started).
* A Code Editor
    * I use VS Code. You can download it [here](https://code.visualstudio.com/).
* Python
    * If you use a Mac you already have Python installed. If you use a Windows PC or Linux, you can download Python [here](https://www.python.org/downloads/).
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
3. Now we're going to create a variable called `upload`. This variable will contain the id of the Upload playlist. Every channel on Youtube has this playlist. Some channels hide it to the users and others leave it visible. This playlist is important because it contains every video the channel has ever published.

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
* Once we have the upload playlist id stored in our `upload` variable we can use it on the `playlist()` method to get the key stats of all the videos from the channel. To learn more about this method click [here](https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.playlistItems.html).

5. One important factor that we need to keep in mind is that every call we make to the Youtube API can only return 50 results, so we need to create a `while` loop that will run the script the number of times necessary to get all the videos. Luckily, the Youtube API offers a parameter inside the `list()` method called `pageToken` that helps us to keep track of how many pages left need to be looped in our code before we get all the videos from the channel. To learn more about this parameter (and the `list()` method inside `playlist()`) click [here](https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.playlistItems.html#list).


```python
# nextPageToken right now is empty but we will change the value our while loop runs. 
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
    
    # Store in a list the first 50 videoIds from the dictionary that we stored on "pl_response"
    vid_ids=[]
    
    for item in pl_response["items"]:
        vid_ids.append(item["contentDetails"]["videoId"])
    
    # You get the stats of the first 50 videos.
    vid_request = youtube.videos().list(
        part=["snippet","statistics"],
        id=",".join(vid_ids)
    )

    vid_response = vid_request.execute()

    # Send the number of views and the URL of each video to the empty list that was declared at the beginning of the code called "videos".
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
```


5. The final step is turning the `video` variable, which currently holds all the information about the channel, into a `pandas` dataframe. To this, we simply use the `from_dict` method on the `video` variable and then, turn that dataframe into a CSV using the `to_csv` method. We can create a variable that stores the name of the channel as a string and use that variable inside the `to_csv` method to store the CSV with the name of the channel.

```python
import pandas as pd

name_of_file= f"{title_of_channel}.csv".replace(" ","_")
pd.DataFrame.from_dict(videos).to_csv(name_of_file)
```
7. If you followed all the tutorial the final result should be something close to this: 

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


