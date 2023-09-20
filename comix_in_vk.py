import requests
import os
import json
import random
from dotenv import load_dotenv


class ErrorWhenPostingComic(TypeError):
    pass


def catch_errors(essence, content):
    if essence == 'error':
        raise ErrorWhenPostingComic(content['error_msg'])
            

def download_image(image_url, path):
    response = requests.get(image_url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def download_comiс(comiс_number):
    url = "https://xkcd.com/{}/info.0.json".format(comiс_number)
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    
    comment_for_comic = comics['alt']
    path_to_comic = 'comiс.jpg'
    download_image(comics['img'], path_to_comic)
    return comment_for_comic


def get_last_comiс_number():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    last_comiс_number = comics['num']
    return last_comiс_number


def get_the_upload_address(access_token, group_id, version):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    version = version
    payload = {
        'v': version,
        'access_token': access_token,
        'group_id': group_id
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    answer = response.json()
    for essence, content in answer.items():
        catch_errors(essence, content)
    address_for_upload = answer['response']['upload_url']
    return address_for_upload


def upload_photos_to_server(access_token, group_id, version):
    file_name = 'comiс.jpg'
    upload_address = get_the_upload_address(access_token, 
        group_id, version)
    with open(file_name, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_address, files=files)
        file.close()
        response.raise_for_status()
        downloaded_photo_info = response.json()
    return downloaded_photo_info


def save_photo_to_album(access_token, group_id, version):
    uploaded_photo_values = upload_photos_to_server(access_token, 
        group_id, version)
    uploaded_photo = uploaded_photo_values['photo']
    photo_server = uploaded_photo_values['server']
    photo_hash = uploaded_photo_values['hash']
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    version = version
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
    for essence, content in saved_photo_info.items():
        catch_errors(essence, content)
    return saved_photo_info


def post_comiс_to_the_wall(access_token, group_id, version):
    last_comiс_number = get_last_comiс_number()
    random_comiс_number = random.randint(0, last_comiс_number)
    message = download_comiс(random_comiс_number)
    saved_photo = save_photo_to_album(vk_app_token, 
        vk_group_id, vk_version)
    photo_id = saved_photo['response'][0]['id']
    owner_id = saved_photo['response'][0]['owner_id']
    version = version
    from_group = 1
    url = 'https://api.vk.com/method/wall.post'
    attachments = 'photo{}_{}'.format(owner_id, photo_id)
    payload = {
        'message': message,
        'attachments': attachments,
        'access_token': access_token,
        'owner_id': -group_id,
        'from_group': from_group,
        'v': version
    }
    response = requests.post(url, params=payload)
    answer = response.json()
    response.raise_for_status()
    for essence, content in answer.items():
        catch_errors(essence, content)


if __name__ == '__main__':
    load_dotenv()
    vk_app_token = os.environ['VK_APP_TOKEN']
    current_vk_version = os.environ['VK_API_VERSION']
    vk_group_id = os.environ['VK_GROUP_ID']
    
    post_comiс_to_the_wall(vk_app_token, vk_group_id, current_vk_version)
    os.remove("comiс.jpg")
