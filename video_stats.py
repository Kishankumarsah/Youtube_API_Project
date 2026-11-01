from json.tool import main
from urllib import request, response
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path='./.env')
CHANNEL_HANDLE = 'MrBeast'
API_KEY = os.getenv('API_KEY')

def get_playlist_id(data):
    try:

        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'
        response = requests.get(url)
        # print(f'Status code: {response.status_code}')
        data= response.json()
        # print(f'JSON response: {json.dumps(data, indent=4)}')
        channel_items = data['items'][0]
        playlist_id = channel_items['contentDetails']['relatedPlaylists']['uploads']
        return playlist_id
    
    except requests.exceptions.RequestException as e:
        # print(f'Error occurred while fetching playlist ID: {e}')
        return e


if __name__ == '__main__':
    playlist_id = get_playlist_id(CHANNEL_HANDLE)
    print(f'Playlist ID: {playlist_id}')  