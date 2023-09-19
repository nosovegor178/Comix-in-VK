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


def upload_photos_to_server(download_adress, file_name):
    with open(file_name, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(download_adress, files=files)
        response.raise_for_status()
        downloaded_photo_info = response.json()
        file.close()
    return downloaded_photo_info


def save_photo_to_album(photo, access_token, server, hash, group_id, version):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    version = version
    group_id = int(group_id)
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


def post_comix_to_the_wall(message, access_token, media_id, 
    owner_id, group_id, version):
    version = version
    group_id = int(group_id) * -1
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
    os.remove("comix.jpg")


if __name__ == '__main__':
    load_dotenv()
    client_id = os.environ['VK_CLIENT_ID']
    vk_app_token = os.environ['VK_APP_TOKEN']
    vk_version = os.environ['VK_API_VERSION']
    vk_group_id = os.environ['VK_GROUP_ID']
    
    last_comix_number = gets_last_comix_number()
    random_comix_number = random.randint(0, last_comix_number)
    comment = download_comix(random_comix_number)
    file_name = 'comix.jpg'
    
    upload_adress = gets_the_upload_adress(vk_app_token, 
        vk_group_id, vk_version)
    uploaded_photo_server_hash = upload_photos_to_server(upload_adress, 
        file_name)
    uploaded_photo = uploaded_photo_server_hash['photo']
    photo_server = uploaded_photo_server_hash['server']
    photo_hash = uploaded_photo_server_hash['hash']
    saved_photo = save_photo_to_album(uploaded_photo, vk_app_token,
                                           photo_server, photo_hash, 
                                           vk_group_id, vk_version)
    photo_id = saved_photo['response'][0]['id']
    owner_id = saved_photo['response'][0]['owner_id']
    
    post_comix_to_the_wall(comment, vk_app_token, photo_id, 
        owner_id, vk_group_id, vk_version)
