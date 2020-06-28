import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
import os
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

class Youtube(object):
    def __init__(self, json_file):
        self.json_file = json_file
        self.client = self.get_client()

    # Gets client information in order to log into Youtube
    def get_client(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        scope = [self.json_file["installed"]["SCOPE_URI"]]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(self.json_file, scope)
        creds = flow.run_console(
            authorization_prompt_message="Your account has not been authorized. Please click this account: {url}")

        return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    # Retrieves playlist ID
    def get_playlist(self):
        request = self.client.playlists().list(part="snippet,contentDetails", maxResults=25, mine=True)
        response = request.execute()
        return response['items'][0]['id']

    # Retrieves liked videos inside of your specified playlist
    def get_liked_videos(self, spotify_obj):
        playlist_id = self.get_playlist()
        request = self.client.playlistItems().list(part="snippet,contentDetails", maxResults=25, playlistId=playlist_id)
        response = request.execute()

        for video in response['items']:
            url = "{}{}".format("https://www.youtube.com/watch?v=", video['contentDetails']['videoId'])
            song = youtube_dl.YoutubeDL({}).extract_info(url, download=False)
            # print(json.dumps(song, indent=4, sort_keys=True))

            if song['track'] is not None and song['artist'] is not None:
                spotify_obj.songs_to_add[video["snippet"]["title"]] = {
                    'song': song['track'],
                    'artist': song['artist'],
                    'spotify_uri': self.convert_url(spotify_obj, song)
                }

    def convert_url(self, spotify, song):
        request_uri = "{}{}".format(spotify.json_data["SPOTIFY"]["API_URI"], "search")

        request_body = {
            'query': 'track:{} artist:{}'.format(song['track'], song['artist']),
            'type': "track",
            'offset': "0",
            'limit': "20"
        }

        request = requests.get(request_uri, params=request_body, headers=spotify.request_header)
        response = request.json()
        result = response["tracks"]["items"]
        uri = result[0]["uri"]

        return uri
