import requests
import json
import os
from res.codes import keys


key = keys['key']
steamidkey = keys['steamidkey']

def write_json_file(date_to_write, fname):
    date_to_write = date_to_write
    fname = fname
    with open(fname, 'w', encoding='utf-8') as json_file:
        json.dump(date_to_write, json_file,
                  ensure_ascii=False, indent=4)
        json_file.close()

def open_json_file(date_to_write, fname):
    date_to_write = date_to_write
    fname = fname
    try:
        open(fname, 'r', encoding='utf-8')
    except FileNotFoundError:
        write_json_file(date_to_write, fname)
    with open(fname, 'r', encoding='utf-8') as read_json_file:
        data_json = json.load(read_json_file)
        read_json_file.close()
    return data_json

def create_avatar(steamid):
    url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={steamid}'
    directory = f"{steamid}"
    parent_dir = f"date\\{steamid}\\"
    path = os.path.join(parent_dir, directory)
    try:
        os.mkdir(path)
    except FileExistsError:        
        pass

    try:
        open(f'date/{steamid}/{steamid}_profile_info.json', 'r')
    except FileNotFoundError:            
        req_profile_info = requests.get(url_profile_info).json()
        if req_profile_info['response']['players'] == []:            
            return "Профиль не найден, либо был удален!"
        if req_profile_info['response']['players'][0]['communityvisibilitystate'] == 1:
            steamid_profile_json = f'date/{steamid}/{steamid}_profile_info.json'
            profile_data_json = open_json_file(req_profile_info, steamid_profile_json)
        elif req_profile_info['response']['players'][0]['communityvisibilitystate'] == 3:
            steamid_profile_json = f'date/{steamid}/{steamid}_profile_info.json'
            profile_data_json = open_json_file(req_profile_info, steamid_profile_json)

    if os.path.exists(f'date/{steamid}/{steamid}_profile_info.json'):
        steamidprofile_json = f'date/{steamid}/{steamid}_profile_info.json'           
        profile_data_json = open_json_file('', steamidprofile_json)
    else:
        req_profile_info = requests.get(url_profile_info).json()
        steamidprofile_json = f'date/{steamid}/{steamid}_profile_info.json'
        profile_data_json = open_json_file(req_profile_info, steamidprofile_json)

    img1 = profile_data_json['response']['players'][0]['avatar']
    img2 = profile_data_json['response']['players'][0]['avatarmedium']
    img3 = profile_data_json['response']['players'][0]['avatarfull']
    if os.path.exists(f'date/{steamid}/{steamid}_avatar.jpg') and os.path.exists(f'date/{steamid}/{steamid}_avatarmedium.jpg') and os.path.exists(f'date/{steamid}/{steamid}_avatarfull.jpg'):
        steamidprofile_json = f'date/{steamid}/{steamid}_profile_info.json'           
        profile_data_json = open_json_file('', steamidprofile_json)
    if not(os.path.exists(f'date/{steamid}/{steamid}_avatar.jpg') and os.path.exists(f'date/{steamid}/{steamid}_avatarmedium.jpg') and os.path.exists(f'date/{steamid}/{steamid}_avatarfull.jpg')):
        req_profile_info = requests.get(url_profile_info).json()
        steamidprofile_json = f'date/{steamid}/{steamid}_profile_info.json'
        profile_data_json = open_json_file(req_profile_info, steamidprofile_json)
    
        p1 = requests.get(img1)
        out1 = open(f"date/{steamid}/{steamid}_avatar.jpg", "wb")
        out1.write(p1.content)
        out1.close()

        p2 = requests.get(img2)
        out2 = open(f"date/{steamid}/{steamid}_avatarmedium.jpg", "wb")
        out2.write(p2.content)
        out2.close()

        p3 = requests.get(img3)
        out3 = open(f"date/{steamid}/{steamid}_avatarfull.jpg", "wb")
        out3.write(p3.content)
        out3.close()
    return "Аватар создан!"
