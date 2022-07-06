import json
import os
import requests
from tqdm import tqdm
import urllib.request
import hashlib
import sys

with open('keys.json', encoding='utf-8') as f:
    data = json.load(f)
    TOKEN = data['vk_token']
    OK_TOKEN = data['ok_token']
    session_secret_key = data['session_secret_key']
    application_key = data['application_key']
    ya_token = data['ya_token']


class YaUploader:
    def __init__(self, token : str):
        self.token = token

    def get_header(self):
        header = {'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : f'OAuth {self.token}'}
        return header

    def create_folder(self, new_folder):
        creation_link = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': new_folder}
        response = requests.put(creation_link, headers= self.get_header(),params=params)


    def get_upload_url(self, path_to_file):
        upload_link = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_header()
        params = {'path' : path_to_file, 'overwrite' : 'True'}
        response = requests.get(upload_link, headers=headers,params=params)
        return response.json()

    def upload(self, file_path: str, upload_folder: str):
        folder = self.create_folder(upload_folder)
        link = self.get_upload_url(path_to_file=(f'/{upload_folder}/{file_path}')).get('href')
        response = requests.put(link, data = open(file_path,'rb'))
        return response

class VKloader:
    def __init__(self):
        self.token = TOKEN
    def get_photos_list(self, user_id):
        dowload_url ='https://api.vk.com/method/photos.get'
        parsms = {'owner_id' : user_id, 'album_id' : 'profile' ,'access_token': self.token, 'v' : '5.131', 'extended' : 1,'photo_sizes' : 1}
        response = requests.get(dowload_url, params=parsms)
        if response.status_code == 200:
            if 'error' in response.json():
                print(f"Ошибка: {response.json()['error']['error_msg']}")
                sys.exit(0)
            else:
                # print(response.json())
                return response.json()
        else:
            print(f"Ошибка: {response.json()['error']['error_msg']}")
            sys.exit(0)

    def backuper(self, u_id):
        reslult = loader.get_photos_list(u_id)
        uploader = YaUploader(ya_token)

        higest_pictures_url_list, likes_list, sizes, for_file = [], [], [], []

        for i in range(len(reslult['response']['items'])):
            higest_pictures_url_list.append(reslult['response']['items'][i]['sizes'][-1]['url'])
            likes_list.append(reslult['response']['items'][i]['likes']['count'])
            sizes.append(reslult['response']['items'][i]['sizes'][-1]['type'])
            for_file.append({'file_name': (str(likes_list[i]) + '.jpg'), 'size': sizes[i]})

        with open('result_VK.json', 'w', encoding='utf-8') as f:
            json.dump(for_file, f)

        for i in tqdm(range(len(higest_pictures_url_list))):
            urllib.request.urlretrieve(higest_pictures_url_list[i], f'{likes_list[i]}.jpg')
            uploader.upload(f'{likes_list[i]}.jpg', u_id)
            os.remove(f'{likes_list[i]}.jpg')

class Ok_download:
    def __init__(self):
        self.token = OK_TOKEN

    def get_md5(self, application_key, user_id, session_secret_key, detectTotalCount=False):
        params = bytes(
            f'application_key={application_key}detectTotalCount={detectTotalCount}fid={user_id}format=jsonmethod=photos.getPhotos{session_secret_key}',
            encoding='utf-8')
        md5_hash = hashlib.md5()
        md5_hash.update(params)
        return md5_hash.hexdigest()

    def get_photo_list(self, application_key, user_id, session_secret_key, count, detectTotalCount=False):
        url = 'https://api.ok.ru/fb.do'
        params = {'application_key': application_key, 'count': count, 'detectTotalCount': detectTotalCount, 'fid': user_id,
                  'format': 'json', 'method': 'photos.getPhotos','sig':self.get_md5(application_key, user_id, session_secret_key, detectTotalCount), 'access_token': self.token}
        response = requests.get(url, params = params)
        if response.status_code == 200:
            if 'error_code' in response.json():
                print(f"Ошибка: {response.json()['error_msg']}")
                sys.exit(0)
            else:
                print(response.json())
                return response.json()
        else:
            print(f"Ошибка: {response.json()['error']['error_msg']}")
            sys.exit(0)

    def backuper(self, u_id):
        uploader = YaUploader(ya_token)
        result = loader.get_photo_list(application_key, u_id, session_secret_key, 100, True)
        pictures_url_list, mark_count,for_file = [], [], []

        for i in tqdm(range(len(result['photos']))):
            pictures_url_list.append(result['photos'][i]['pic640x480'])
            mark_count.append(result['photos'][i]['mark_count'])
            for_file.append({'file_name': (str(mark_count[i]) + '.jpg'), 'size': 'pic640x480'})
            urllib.request.urlretrieve(pictures_url_list[i], f'{mark_count[i]}.jpg')
            uploader.upload(f'{mark_count[i]}.jpg', u_id)
            os.remove(f'{mark_count[i]}.jpg')
        with open('result_Ok.json', 'w', encoding='utf-8') as f:
            json.dump(for_file, f)



if __name__ == '__main__':
    choice = int(input('Введите идентификатор социальной сети (1 - VK, 2 - OK:)'))
    if choice == 1:
        u_id = int(input('Введте ID пользователя: '))
        loader = VKloader()
        reslult = loader.backuper(u_id)
    elif choice == 2:
        u_id = int(input('Введте ID пользователя: '))
        loader = Ok_download()
        result = loader.backuper(u_id)
    else:
        print('Все сломалось....')
