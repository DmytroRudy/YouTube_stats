import pandas as pd
from googleapiclient.discovery import build


class Downloader:


    def __init__(self, channel_id, api_key):

        #Creating youtube object

        self.__channel_id = channel_id

        api_service_name = "youtube"
        api_version = "v3"
        #Initialising a downloader
        self.__youtube = build(api_service_name, api_version, developerKey=api_key)

        #Getting stats

        request = self.__youtube.channels().list(
            part='snippet, contentDetails, statistics',
            id=self.__channel_id
        )

        response = request.execute()

        self.stats_data = dict(Name=response['items'][0]['snippet']['title'],
                               Subs=response['items'][0]['statistics']['subscriberCount'],
                               Views=response['items'][0]['statistics']['viewCount'],
                               Videos_Count=response['items'][0]['statistics']['videoCount'],
                               Playlist_id= response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])

        #Getting Playlist id

        self.__playlist_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        #Getting video_ids

        request = self.__youtube.playlistItems().list(
            part ='contentDetails',
            playlistId = self.__playlist_id,
            maxResults = 50
        )

        response = request.execute()

        self.__video_ids=[]

        for i in range(len(response['items'])):
            self.__video_ids.append(response['items'][i]['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        more_pages=True

        while more_pages:
            if next_page_token is None:
                more_pages = False
            else:request = self.__youtube.playlistItems().list(
                part='contentDetails',
                playlistId=self.__playlist_id,
                maxResults = 50,
                pageToken = next_page_token
            )
            response = request.execute()
            for i in range(len(response['items'])):
                self.__video_ids.append(response['items'][i]['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')


        #Creating dataframes

        video_stats = []


        for i in range(0, len(self.__video_ids), 50):
            request = self.__youtube.videos().list(
                part = 'snippet, statistics',
                id=','.join(self.__video_ids[i:i+50])
            )

            response = request.execute()

            for video in  response['items']:
                video_stat = dict(Title = video['snippet']['title'],
                                  Publish_date = video['snippet']["publishedAt"],
                                  Views =  video['statistics']["viewCount"],
                                  Likes = video['statistics']["likeCount"],
                                  Comments = video['statistics']["commentCount"],
                                  )
                video_stats.append(video_stat)

        self.videos_data = pd.DataFrame(video_stats)
        self.videos_data['Publish_date'] = pd.to_datetime(self.videos_data['Publish_date'])
        self.videos_data['Views'] = pd.to_numeric(self.videos_data['Views'])
        self.videos_data['Likes'] = pd.to_numeric(self.videos_data['Likes'])
        self.videos_data['Comments'] = pd.to_numeric(self.videos_data['Comments'])



    def get_video_ids(self):
        return self.__video_ids




#%%

#%%
