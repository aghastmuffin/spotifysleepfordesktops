import requests
import webbrowser
import os
import websockets
import asyncio

class SpotifyAuthenticator:
    def __init__(self, client_id, redirect_uri, scope):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.authorization_code = ""

    async def _websocket_handler(self, websocket, path):
        async for message in websocket:
            self.authorization_code = message
            print(self.authorization_code)
            await websocket.send("200")
            asyncio.get_event_loop().stop()

    def open_authentication_window(self):
        auth_url = (
            f'https://accounts.spotify.com/authorize?client_id={self.client_id}'
            f'&response_type=code&redirect_uri={self.redirect_uri}&scope={self.scope}'
        )
        print("Opening authentication window...")
        webbrowser.open(auth_url)

    def get_authorization_code(self):
        try:
            start_server = websockets.serve(
                self._websocket_handler, "localhost", 8765)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
        except Exception as e:
            print(f"WSS An error occurred: {e}")
            self.authorization_code = input(
                "Enter the code from the redirected URL: ")

    def exchange_code_for_token(self, client_secret):
        token_url = 'https://accounts.spotify.com/api/token'
        token_data = {
            'grant_type': 'authorization_code',
            'code': self.authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': client_secret,
        }
        response = requests.post(token_url, data=token_data)

        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info['access_token']
            print("Access Token:", access_token)
            return access_token
        else:
            print("Error obtaining access token:", response.text)
            return None



def init_spotify_auth(client_id, redirect_uri, scope):
    return SpotifyAuthenticator(client_id, redirect_uri, scope)

def get_devices(access_token):
    headers = {
    'Authorization': f'Bearer {access_token}',
    }
    a = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers)
    if a.status_code == 200:
        return a.json()
def pause(access_token, deviceid):
    headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
    }
    data = {'device_ids': [deviceid], 'pause': True}
    a = requests.put("https://api.spotify.com/v1/me/player/pause", headers=headers, json=data)
    if a.status_code == 204: #different status code from spotifys api (DOCS)
        return 200
    else:
        print("error")