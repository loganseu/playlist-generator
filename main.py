import requests, json, base64, os

class Authentication:
    def __init__(self):
        self.BASE_URL = r"https://api.spotify.com/v1/"
        self.TOKEN_URL = r"https://accounts.spotify.com/api/token"
        self.AUTH_URL = r"https://accounts.spotify.com/authorize"

        self.client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        self.clientsecret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('SPOTIFY_REDIRECT_URI')
        self.scope = os.environ.get('SPOTIFY_SCOPE')
        self.state = os.environ.get('SPOTIFY_STATE')
        self.code = os.environ.get('SPOTIFY_AUTH_CODE')
        self.access_token = os.environ.get('SPOTIFY_ACCESS_TOKEN')
        self.refresh_token = os.environ.get('SPOTIFY_REFRESH_TOKEN')

        self.auth_str_64 = base64.urlsafe_b64encode('{}:{}'.format(self.client_id, self.clientsecret).encode()).decode()
        self.headers = {'Authorization': 'Basic {0}'.format(self.auth_str_64)}

        self.auth_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'state': self.state
        }
        self.access_token_post_body = {
            'code': self.code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
                            }
        self.refresh_token_post_body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
                            }

    def Get_Authorization(self):
        #1 - gets authorization
        get_authorization = requests.get(url=self.AUTH_URL, params=self.auth_params)
        #response_data = json.loads(get_authorization.text)
        print(get_authorization.url)

    # Returns object containing access and refresh tokens. Call this once
    def Get_Tokens(self):
        response = requests.post(self.TOKEN_URL, data=self.access_token_post_body, headers=self.headers)
        stuff = json.loads(response.text)
        self.refresh_token = stuff['refresh_token']
        self.access_token = stuff['access_token']

    # Updates access token
    def Update_Access_Token(self):
        response = requests.post(self.TOKEN_URL, data=self.refresh_token_post_body, headers=self.headers)
        response_data = json.loads(response.text)
        print(response_data)

    def Test(self):
        playlist = 	r"https://api.spotify.com/v1/users/"
        headers = {'Authorization': 'Bearer ' + self.access_token}
        f = requests.get(playlist, headers=headers)
        print(f.text)

# A = Authentication()
# A.Get_Authorization()
# A.Get_Tokens()
# A.Update_Access_Token()
# A.Test()