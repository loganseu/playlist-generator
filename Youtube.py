import requests
import webbrowser
import json
import urllib.parse as url
import googleapiclient.errors
import youtube_dl
import os
import googleapiclient.discovery
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI, client

class Youtube(object):
    def __init__(self, json_file):
        self.json_data = json_file

        self.auth_uri = "{}{}".format("https://accounts.google.com/o/oauth2/auth?",
                                      url.unquote(url.urlencode({"client_id": self.json_data["installed"]["client_id"],
                                                                   "response_type": self.json_data["spotify"]["response_type"],
                                                                   "redirect_uri": self.json_data["spotify"]["redirect_uri"],
                                                                   "scope": "https://www.googleapis.com/auth/youtube.readonly",
                                                                   "state": self.json_data["spotify"]["state"]})))

        # self.get_tokens()
        self.update_access_token()
        self.client = self.get_client()

    # Gets client information in order to log into Youtube
    def get_client(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        scope = [self.json_data["installed"]["scope"]]

        credentials = client.OAuth2Credentials(
            access_token=self.json_data["installed"]["access_token"],
            client_id=self.json_data["installed"]["client_id"],
            client_secret=self.json_data["installed"]["client_secret"],
            refresh_token=self.json_data["installed"]["refresh_token"],
            token_expiry=self.json_data["installed"]["token_expiry"],
            token_uri=GOOGLE_TOKEN_URI,
            user_agent=None,
            revoke_uri=GOOGLE_REVOKE_URI)

        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    def get_tokens(self):
        # if tokens expire, get auth code
        webbrowser.open(self.auth_uri, autoraise=True)

        self.json_data["installed"]["code"] = input("Enter the code you receive here: ")
        with open("config.json", "w") as json_file:
            json.dump(self.json_data, json_file, indent=4, sort_keys=True)

        access_token_post_body = {
            "code": self.json_data["installed"]["code"],
            "client_id": self.json_data["installed"]["client_id"],
            "client_secret": self.json_data["installed"]["client_secret"],
            "grant_type": "authorization_code",
            "redirect_uri": self.json_data["spotify"]["redirect_uri"]
        }

        request = requests.post(self.json_data["installed"]["token_uri"], data=access_token_post_body)
        response = json.loads(request.text)

        self.json_data["installed"]["access_token"] = response["access_token"]
        self.json_data["installed"]["refresh_token"] = response["refresh_token"]

        with open("config.json", "w") as json_file:
            json.dump(self.json_data, json_file, indent=4, sort_keys=True)

    def update_access_token(self):
        refresh_token_post_body = {
            "client_id": self.json_data["installed"]["client_id"],
            "client_secret": self.json_data["installed"]["client_secret"],
            "refresh_token": self.json_data["installed"]["refresh_token"],
            "grant_type": "refresh_token"
        }

        request = requests.post(self.json_data["installed"]["token_uri"], data=refresh_token_post_body)
        response = json.loads(request.text)

        self.json_data["installed"]["access_token"] = response["access_token"]
        self.json_data["installed"]["token_expiry"] = response["expires_in"]
        with open("config.json", "w") as json_file:
            json.dump(self.json_data, json_file, indent=4, sort_keys=True)

    # Retrieves playlist ID
    def get_playlist(self):
        request = self.client.playlists().list(part="snippet,contentDetails", maxResults=25, mine=True)
        response = request.execute()
        return response["items"][0]["id"]

    # Retrieves liked videos inside of your specified playlist
    def get_liked_videos(self, spotify_obj):
        playlist_id = self.get_playlist()
        request = self.client.playlistItems().list(part="snippet,contentDetails", maxResults=25, playlistId=playlist_id)
        response = request.execute()

        for video in response["items"]:
            url = "{}{}".format("https://www.youtube.com/watch?v=", video["contentDetails"]["videoId"])
            song = youtube_dl.YoutubeDL({}).extract_info(url, download=False)
            # print(json.dumps(song, indent=4, sort_keys=True))

            if song["track"] is not None and song["artist"] is not None:
                spotify_obj.songs_to_add[video["snippet"]["title"]] = {
                    "song": song["track"],
                    "artist": song["artist"],
                    "spotify_uri": self.convert_url(spotify_obj, song)
                }

    def convert_url(self, spotify, song):
        request_uri = "{}{}".format(spotify.json_data["spotify"]["api_uri"], "search")

        request_body = {
            "query": "track:{} artist:{}".format(song["track"], song["artist"]),
            "type": "track",
            "offset": "0",
            "limit": "20"
        }

        request = requests.get(request_uri, params=request_body, headers=spotify.request_header)
        response = request.json()
        result = response["tracks"]["items"]
        uri = result[0]["uri"]

        return uri