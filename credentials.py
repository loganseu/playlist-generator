import requests, json, base64, os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
import pickle
import webbrowser

class Spotify:
    def __init__(self):
        # Client Properties
        self.access_token = os.environ.get('SPOTIFY_ACCESS_TOKEN')
        self.client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        self.client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        self.code = os.environ.get('SPOTIFY_AUTH_CODE')
        self.refresh_token = os.environ.get('SPOTIFY_REFRESH_TOKEN')
        self.scope = os.environ.get('SPOTIFY_SCOPE')
        self.state = os.environ.get('SPOTIFY_STATE')

        # Authorization code
        self.auth_str_64 = base64.urlsafe_b64encode('{}:{}'.format(self.client_id, self.client_secret).encode()).decode()
        self.headers = {'Authorization': 'Basic {0}'.format(self.auth_str_64)}

        # URIs
        self.base_uri = r"https://api.spotify.com/v1/"
        self.token_uri = r"https://accounts.spotify.com/api/token"
        self.redirect_uri = os.environ.get('REDIRECT_URI')
        self.auth_uri = r'https://accounts.spotify.com/authorize' + '?client_id=' + self.client_id + '&response_type=code&redirect_uri=' + self.redirect_uri + '&scope=user-read-private&state=' + self.state

    # Gets access and refresh tokens, updates them
    def Get_Tokens(self):
        # if tokens expire, get auth code
        webbrowser.open(self.auth_uri, autoraise=True)

        self.code = input("Enter the code you receive here: ")
        access_token_post_body = {
            'code': self.code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
                            }

        request = requests.post(self.token_uri, data=access_token_post_body, headers=self.headers)
        response = json.loads(request.text)

        self.refresh_token = response['refresh_token']
        self.access_token = response['access_token']

    # Updates access token using refresh token
    def Update_Access_Token(self):
        refresh_token_post_body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
                            }

        request = requests.post(self.token_uri, data=refresh_token_post_body, headers=self.headers)
        response_data = json.loads(request.text)
        self.access_token = response_data['access_token']

    def Test(self):
        playlist = 	r'https://api.spotify.com/v1/users/'
        headers = {'Authorization': 'Bearer ' + self.access_token}
        f = requests.get(playlist, headers=headers)
        print(f.text)



class Youtube:
    def __init__(self):

        # URIs
        self.scope_uri = r"https://www.googleapis.com/auth/youtube.readonly"
        self.redirect_uri = os.environ.get('REDIRECT_URI')

        # Client Properties
        self.access_token = os.environ.get('YOUTUBE_ACCESS_TOKEN')
        self.api_key = os.environ.get('YOUTUBE_API_KEY')
        self.client_info = os.environ.get('YOUTUBE_CLIENT_INFO')
        self.get_client_info_json = json.loads(open(self.client_info, "r").read())
        self.client_id = self.get_client_info_json['installed']['client_id']
        self.client_secret = self.get_client_info_json['installed']['client_secret']
        self.credentials = os.path.join(os.environ.get('YOUTUBE_CREDENTIALS'), 'client_' + self.client_id + '_credentials' + '.pickle')
        self.headers = {'Authorization': 'Bearer ' + ""}

        # Client
        self.client = self.Get_Client()

    # Gets client information in order to log into Youtube
    def Get_Client(self):
        if (os.path.isfile(self.credentials)):
            creds = pickle.load(open(self.credentials, "rb"))

        else:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
            scope = [self.scope_uri]
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(self.client_info, scope)
            creds = flow.run_console(authorization_prompt_message="Your account has not been authorized. Please click this account: {url}")

            # Saves credentials object for future reference, so you don't have to authorize every time
            with open(self.credentials, 'wb') as handle:
                pickle.dump(creds, handle)

        return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    # Retrieves playlist ID
    def Get_Playlist(self):
        request = self.client.playlists().list(part="snippet,contentDetails", maxResults=25, mine=True)
        response = request.execute()
        return response['items'][0]['id']

    #Retrieves liked videos inside of your specified playlist
    def Get_Liked_Videos(self):
        playlist_id = self.Get_Playlist()
        request = self.client.playlistItems().list(part="snippet,contentDetails", maxResults=25, playlistId=playlist_id)
        response = request.execute()

        list_of_songs = []

        for video in response['items']:
            url = "https://www.youtube.com/watch?v=" + video['contentDetails']['videoId']

            video_to_song = youtube_dl.YoutubeDL({}).extract_info(url, download=False)
            # print(json.dumps(song, indent=4, sort_keys=True))
            song_info = {
                'song': video_to_song['track'],
                'artist': video_to_song['artist'],
                'url': url
            }

            list_of_songs.append(song_info)

        for song in list_of_songs:
            print(song['song'])
            print(song['artist'])
            print(song['url'])

A = Spotify()
A.Get_Tokens()
A.Update_Access_Token()
A.Test()
# x = Youtube()
# x.Get_Liked_Videos()