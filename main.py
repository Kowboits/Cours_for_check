import json
import os
import requests
from tqdm import tqdm
import urllib.request

with open('token.txt', encoding='utf-8') as f:
    TOKEN = f.readline()
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
        parsms = {'user_ids' : user_id, 'album_id' : 'profile' ,'access_token': self.token, 'v' : '5.131', 'extended' : 1,'photo_sizes' : 1}
        response = requests.get(dowload_url, params=parsms)
        return response.json()

if __name__ == '__main__':
    u_id = int(input('Введте ID пользователя')) #600205522
    loader = VKloader()
    reslult = loader.get_photos_list(u_id)
    higest_pictures_url_list, likes_list, sizes, for_file = [], [], [], []
    token = 'AQAAAAAscO-rAADLW0smk4swSUrMjUeMsadsmTU'
    uploader = YaUploader(token)

    for i in range(len(reslult['response']['items'])):
        higest_pictures_url_list.append(reslult['response']['items'][i]['sizes'][-1]['url'])
        likes_list.append(reslult['response']['items'][i]['likes']['count'])
        sizes.append(reslult['response']['items'][i]['sizes'][-1]['type'])
        for_file.append({'file_name': (str(likes_list[i]) + '.jpg'), 'size': sizes[i]})

    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(for_file, f)

    for i in tqdm(range(len(higest_pictures_url_list))):
        urllib.request.urlretrieve(higest_pictures_url_list[i], f'{likes_list[i]}.jpg')
        uploader.upload(f'{likes_list[i]}.jpg', u_id)
        os.remove(f'{likes_list[i]}.jpg')