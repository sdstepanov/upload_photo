import requests
import json
import logging
import time
from collections import Counter

Token = ''
Id_user = ''

logging.basicConfig(level=logging.INFO, format='%(message)s')


class Vk_photos:

    def __init__(self, token, id_user):
        self.url = 'https://api.vk.com/method/photos.get'
        self.token = token
        self.id_user = id_user
        self.folders = ['profile', 'wall', 'saved']
        self.folder = None
        self.data_photo = {}
        self.data_upload = []
        self.photo_json = []
        self.params = {
            'owner_id': f'{self.id_user}',
            'extended': '1',
            'access_token': 'f9faf62df6ab59dc42812b0a1e7b68acb24934591a3a9b3b96472713a1f0142c691b854b3ceeaff1473a6',
            'v': '5.131'
        }
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def get_album_vk(self):
        logging.info(f'The start uploading photos from VK to YandexDisk!')
        self.create_folders()
        for self.folder in self.folders:
            self.params['album_id'] = self.folder
            self.data_photo = {'photo_name': [], 'photo_url': [], 'photo_date': [], 'photo_size': []}
            self.data_upload = []
            self.get_data_photos()
        self.get_json_file()
        logging.info(f'All photos have been upload successfully!')

    def get_data_photos(self):
        logging.info(f'Getting data of photos from "{self.folder}" album...')
        time.sleep(1)
        response = requests.get(self.url, params=self.params).json()
        for data in response['response']['items']:
            self.data_photo['photo_name'] += [data['likes']['count']]
            self.data_photo['photo_url'] += [data['sizes'][-1]['url']]
            self.data_photo['photo_date'] += [data['date']]
            self.data_photo['photo_size'] += [data['sizes'][-1]['type']]
        logging.info(f'The data of photos from "{self.folder}" album has been successfully received!')
        time.sleep(1)
        self.get_data_upload()
        self.get_data_json()
        self.upload()

    def get_data_upload(self):
        logging.info(f'Getting data of upload photos from "{self.folder}" album...')
        time.sleep(1)
        ph_name = self.data_photo['photo_name']
        ph_date = self.data_photo['photo_date']
        ph_url = self.data_photo['photo_url']
        counter = Counter(ph_name)
        for num, _ in enumerate(ph_name):
            for count in counter.keys():
                if count == ph_name[num] and counter.get(count) > 1:
                    self.data_upload += [(f'{ph_name[num]}_{ph_date[num]}', ph_url[num])]
                    break
                elif count == ph_name[num] and counter.get(count) == 1:
                    self.data_upload += [(f'{ph_name[num]}', ph_url[num])]
                    break
        logging.info(f'Getting data of upload photos from "{self.folder}" album has been successfully!')
        time.sleep(1)

    def create_folders(self):
        logging.info(f'Creating new folders on "YandexDisk"...')
        time.sleep(1)
        create_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        for folder in self.folders:
            params = {'path': f'{folder}'}
            requests.put(create_url, headers=self.headers, params=params)
        logging.info(f'Creating has been successfully!')
        time.sleep(1)

    def upload(self):
        logging.info(f'Uploading photos to "{self.folder}" folder...')
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        for photo in self.data_upload:
            params = {'path': f'{self.folder}/{photo[0]}.jpg', 'url': photo[1]}
            requests.post(upload_url, params=params, headers=self.headers)
        logging.info(f'Uploading has been successfully!')

    def get_data_json(self):
        for count, photo in enumerate(self.data_upload):
            self.photo_json += [{'file_name': f'{photo[0]}.jpg', 'size': f'{self.data_photo["photo_size"][count]}'}]

    def get_json_file(self):
        with open('ph.json', 'w') as f:
            json.dump(self.photo_json, f)


if __name__ == '__main__':
    photo_id = Vk_photos(Token, Id_user)
    photo_id.get_album_vk()
