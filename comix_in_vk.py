import requests
import os
import json
import random
from dotenv import load_dotenv


def download_image(image_url, path):
    response = requests.get(image_url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def get_adress_for_download(access_token):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    version = 5.131
    group_id = 222396924
    payload = {
        'v': version,
        'access_token': access_token,
        'group_id': group_id
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    answer = response.json()
    adress_for_download = answer['response']['upload_url']
    return adress_for_download


def download_photos_to_server(download_adress, file_name):
    with open(file_name, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(download_adress, files=files)
        response.raise_for_status()
        downloaded_photo_info = response.json()
    return downloaded_photo_info


def save_photo_to_album(photo, access_token, server, hash):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    version = 5.131
    group_id = 222396924
    payload = {
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': hash,
        'access_token': access_token,
        'v': version
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    saved_photo_info = response.json()
    return saved_photo_info


def download_comics_and_get_comment(comix_number):
    url = "https://xkcd.com/{}/info.0.json".format(comix_number)
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    
    comment_for_comic = comics['alt']
    path_to_comic = 'comix.jpg'
    download_image(comics['img'], path_to_comic)
    return comment_for_comic


def get_last_comix_number():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    last_comix_number = comics['num']
    return last_comix_number


def post_comix_to_the_wall(message, access_token, media_id, owner_id):
    version = 5.131
    group_id = -222396924
    from_group = 1
    url = 'https://api.vk.com/method/wall.post'
    attachments = 'photo{}_{}'.format(owner_id, media_id)
    payload = {
        'message': message,
        'attachments': attachments,
        'access_token': access_token,
        'owner_id': group_id,
        'from_group': from_group,
        'v': version
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    

if __name__ == '__main__':
    load_dotenv()
    my_secret = os.environ['CLIENT_ID_VK']
    vk_app_token = os.environ['VK_APP_TOKEN']
    
    last_comix_number = get_last_comix_number()
    random_comix_number = random.randint(0, last_comix_number)
    comment = download_comics_and_get_comment(random_comix_number)
    file_name = 'comix.jpg'
    
    download_adress = get_adress_for_download(vk_app_token)
    downloaded_photo_info = download_photos_to_server(download_adress, file_name)
    downloaded_photo = downloaded_photo_info['photo']
    photo_server = downloaded_photo_info['server']
    photo_hash = downloaded_photo_info['hash']
    saved_photo_info = save_photo_to_album(downloaded_photo, vk_app_token,
                                           photo_server, photo_hash)
    photo_id = saved_photo_info['response'][0]['id']
    owner_id = saved_photo_info['response'][0]['owner_id']
    post_comix_to_the_wall(comment, vk_app_token, photo_id, owner_id)
    os.remove("comix.jpg")
    
