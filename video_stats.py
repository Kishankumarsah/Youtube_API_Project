from json.tool import main
from urllib import request, response
import os
import requests
from dotenv import load_dotenv
from datetime import date, datetime
import json

load_dotenv(dotenv_path='./.env')
CHANNEL_HANDLE = 'MrBeast'
API_KEY = os.getenv('API_KEY')
maxResults = 50

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


def get_video_ids(playlistId):

    video_ids = []
    pageToken = None
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}'
    
    try:
        while True:
            url = base_url
            if pageToken:
                url += f'&pageToken={pageToken}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items',[]):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            pageToken = data.get('nextPageToken')
            if not pageToken:
                break
            return video_ids
    
    
    except requests.exceptions.RequestException as e:
        # print(f'Error occurred while fetching video IDs: {e}')
        return e


def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_ids, batch_size):
        for i in range(0, len(video_ids), batch_size):
            yield video_ids[i:i + batch_size]

    try:
        for batch in batch_list(video_ids, 50):

            ids = ','.join(batch)

            url = 'https://youtube.googleapis.com/youtube/v3/videos'

            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': ids,
                'key': API_KEY
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'error' in data:
                raise ValueError(data['error'])

            for item in data.get('items', []):

                video_id = item.get('id')
                snippet = item.get('snippet', {})
                contentDetails = item.get('contentDetails', {})
                statistics = item.get('statistics', {})

                video_data = {
                    'video_id': video_id,
                    'title': snippet.get('title'),
                    'published_at': snippet.get('publishedAt'),
                    'duration': contentDetails.get('duration'),
                    'view_count': statistics.get('viewCount'),
                    'like_count': statistics.get('likeCount'),
                    'comment_count': statistics.get('commentCount')
                }

                extracted_data.append(video_data)

        return extracted_data

    except (requests.exceptions.RequestException, ValueError) as e:
        print(f'Error occurred while extracting video data: {e}')
        return []
# def extract_video_data(video_ids):
#     extracted_data = []
#     def batch_list(video_ids, batch_size):
#         for i in range(0, len(video_ids), batch_size):
#             yield video_ids[i:i + batch_size]

#     try:
#         for batch in batch_list(video_ids, 50):
#             ids = ','.join(batch)
#             url = f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id={ids}&key={API_KEY}'
#             response = requests.get(url)
#             data = response.json()
#             for item in data.get('items', []):
#                 video_id = item['id']
#                 snippet = item['snippet']
#                 contentDetails = item.get('contentDetails', {})
#                 statistics = item.get('statistics', {})

#                 video_data = {
#                     'video_id': video_id,
#                     'title': snippet.get('title'),
#                     # 'description': snippet.get('description'),
#                     'published_at': snippet.get('publishedAt'),
#                     # 'channel_title': snippet.get('channelTitle'),
#                     'duration': contentDetails.get('duration'),
#                     'view_count': statistics.get('viewCount',None),
#                     'like_count': statistics.get('likeCount',None),
#                     'comment_count': statistics.get('commentCount',None),
#                 }
#             extracted_data.append(video_data)
#         return extracted_data
#     except requests.exceptions.RequestException as e:
#         # print(f'Error occurred while extracting video data: {e}')
#         return e 

def save_data_to_json(extracted_data):
    file_path = f'./data/YT_data_{date.today()}.json'
    with open(file_path, 'w',encoding ='utf-8') as json_file:
        json.dump(extracted_data, json_file, indent=4,ensure_ascii=False)
         

if __name__ == '__main__':
    playlist_id = get_playlist_id(CHANNEL_HANDLE)
    print(f'Playlist ID: {playlist_id}')  
    video_ids = get_video_ids(playlist_id)
    print(f'Video IDs: {video_ids}')
    extracted_data = extract_video_data(video_ids)
    print(f'Extracted Data: {extracted_data}')
    save_data_to_json(extracted_data)