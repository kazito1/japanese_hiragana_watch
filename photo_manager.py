import os
import datetime
import random
import requests
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
API_BASE_URL = 'https://photoslibrary.googleapis.com/v1'

class PhotoManager:
    SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
    API_BASE_URL = 'https://photoslibrary.googleapis.com/v1'
    MAX_CACHE_SIZE = 10  # Maximum number of photos to keep in cache

    def __init__(self, cache_dir='photo_cache', months_range=12):
        self.creds = self.get_credentials()
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.photo_list = []
        self.clean_cache()
        self.months_range = months_range

    def get_credentials(self):
        creds = None
        if os.path.exists('token.json'):
            with open('token.json', 'r') as token:
                cred_data = json.load(token)
            creds = Credentials(
                token=cred_data['token'],
                refresh_token=cred_data['refresh_token'],
                token_uri=cred_data['token_uri'],
                client_id=cred_data['client_id'],
                client_secret=cred_data['client_secret'],
                scopes=cred_data['scopes']
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(json.dumps({
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }))
        return creds

    def get_recent_photos(self):
        print("Fetching recent favorite photos")
        one_year_ago = datetime.now() - timedelta(days=365)
        body = {
            'filters': {
                'dateFilter': {
                    'ranges': [{
                        'startDate': {
                            'year': one_year_ago.year,
                            'month': one_year_ago.month,
                            'day': one_year_ago.day
                        },
                        'endDate': {
                            'year': datetime.now().year,
                            'month': datetime.now().month,
                            'day': datetime.now().day
                        }
                    }]
                },
                'featureFilter': {
                    'includedFeatures': ['FAVORITES']
                }
            },
            'pageSize': 100
        }
        headers = {
            'Authorization': f'Bearer {self.creds.token}',
            'Content-Type': 'application/json'
        }
        response = None
        try:
            response = requests.post(f'{self.API_BASE_URL}/mediaItems:search', json=body, headers=headers)
            response.raise_for_status()
            return response.json().get('mediaItems', [])
        except requests.RequestException as e:
            print(f"Error fetching photos: {e}")
            if response:
                print(f"Response content: {response.content}")
            return []

    def download_photo(self, media_item):
        download_url = f"{media_item['baseUrl']}=d"
        filename = f"{media_item['id']}.jpg"
        filepath = os.path.join(self.cache_dir, filename)
        if not os.path.exists(filepath):
            try:
                response = requests.get(download_url)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                self.clean_cache()
            except requests.RequestException as e:
                print(f"Error downloading photo: {e}")
                return None
        return filepath

    def clean_cache(self):
        cached_files = [os.path.join(self.cache_dir, f) for f in os.listdir(self.cache_dir) if f.endswith('.jpg')]
        cached_files.sort(key=os.path.getmtime)  # Sort files by modification time
        while len(cached_files) > self.MAX_CACHE_SIZE:
            oldest_file = cached_files.pop(0)
            os.remove(oldest_file)
            print(f"Removed old cached file: {oldest_file}")

    def get_random_photo(self):
        if not self.photo_list:
            self.photo_list = self.get_recent_photos()
        
        if self.photo_list:
            photo = random.choice(self.photo_list)
            self.photo_list.remove(photo)  # Ensure we don't repeat photos until we've gone through all of them
            return self.download_photo(photo)
        else:
            print("No favorite photos found. Please mark some photos as favorites in Google Photos.")
            return None
