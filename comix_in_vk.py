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


def download_comix(comix_number):
    url = "https://xkcd.com/{}/info.0.json".format(comix_number)
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    
    comment_for_comic = comics['alt']
    path_to_comic = 'comix.jpg'
    download_image(comics['img'], path_to_comic)
    return comment_for_comic


def gets_last_comix_number():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    last_comix_number = comics['num']
    return last_comix_number


def gets_the_upload_adress(access_token, group_id, version):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    version = version
    group_id = int(group_id)
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


def upload_photos_to_server(access_token, group_id, version):
    file_name = 'comix.jpg'
    upload_adress = gets_the_upload_adress(access_token, 
        group_id, version)
    with open(file_name, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_adress, files=files)
        response.raise_for_status()
        downloaded_photo_info = response.json()
        file.close()
    return downloaded_photo_info


def save_photo_to_album(access_token, group_id, version):
    uploaded_photo_values = upload_photos_to_server(access_token, 
        group_id, version)
    uploaded_photo = uploaded_photo_values['photo']
    photo_server = uploaded_photo_values['server']
    photo_hash = uploaded_photo_values['hash']
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    version = version
    group_id = int(group_id)
    payload = {
        'group_id': group_id,
        'photo': uploaded_photo,
        'server': photo_server,
        'hash': photo_hash,
        'access_token': access_token,
        'v': version
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    saved_photo_info = response.json()
    return saved_photo_info


def post_comix_to_the_wall(access_token, group_id, version):
    last_comix_number = gets_last_comix_number()
    random_comix_number = random.randint(0, last_comix_number)
    message = download_comix(random_comix_number)
    saved_photo = save_photo_to_album(vk_app_token, 
        vk_group_id, vk_version)
    photo_id = saved_photo['response'][0]['id']
    owner_id = saved_photo['response'][0]['owner_id']
    version = version
    group_id = int(group_id) * -1
    from_group = 1
    url = 'https://api.vk.com/method/wall.post'
    attachments = 'photo{}_{}'.format(owner_id, photo_id)
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
    os.remove("comix.jpg")


if __name__ == '__main__':
    load_dotenv()
    vk_app_token = os.environ['VK_APP_TOKEN']
    vk_version = os.environ['VK_API_VERSION']
    vk_group_id = os.environ['VK_GROUP_ID']

    
    post_comix_to_the_wall(vk_app_token, vk_group_id, vk_version)
