import json
import os
from datetime import date

import requests

from res.codes import keys

KEY = keys['key']

# ! today = date.today()
today_date = date.today()  # ! today.strftime("%b-%d-%Y")


def write_json_file(date_to_write, fname):
    with open(fname, 'w', encoding='utf-8') as json_file:
        json.dump(date_to_write, json_file,
                  ensure_ascii=False, indent=4)


def open_json_file(fname):
    with open(fname, 'r', encoding='utf-8') as read_json_file:
        return json.load(read_json_file)


def create_avatar(steamid):
    url_profile_info = (
        'https://api.steampowered.com/ISteamUser/'
        f'GetPlayerSummaries/v2/?key={KEY}&steamids={steamid}')
    steamid_profile_json = (
        f'date/{steamid}/{steamid}'
        f'_profile_info_{today_date}.json')
    directory = f'{steamid}'
    parent_dir = f'date\\{steamid}\\'
    path = os.path.join(parent_dir, directory)
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

    try:
        open(f'date/{steamid}/{steamid}_profile_info_{today_date}.json', 'r')
    except FileNotFoundError:
        req_profile_info = requests.get(url_profile_info).json()
        if req_profile_info['response']['players'] == []:
            return "Профиль не найден, либо был удален!"
        if (
            req_profile_info['response']['players'][0]
            ['communityvisibilitystate'] == 1
        ):
            profile_data_json = open_json_file(steamid_profile_json)
        elif (
            req_profile_info['response']['players'][0]
            ['communityvisibilitystate'] == 3
        ):
            profile_data_json = open_json_file(steamid_profile_json)

    if os.path.exists(
        f'date/{steamid}/{steamid}_profile_info_{today_date}.json'
    ):
        profile_data_json = open_json_file(steamid_profile_json)
    else:
        req_profile_info = requests.get(url_profile_info).json()
        write_json_file(req_profile_info, steamid_profile_json)
        profile_data_json = open_json_file(steamid_profile_json)

    img1 = profile_data_json['response']['players'][0]['avatar']
    img2 = profile_data_json['response']['players'][0]['avatarmedium']
    img3 = profile_data_json['response']['players'][0]['avatarfull']
    if os.path.exists(
        f'date/{steamid}/{steamid}_avatar_{today_date}.jpg'
        ) and os.path.exists(
            f'date/{steamid}/{steamid}_avatarmedium_{today_date}.jpg'
            ) and os.path.exists(
                f'date/{steamid}/{steamid}_avatarfull_{today_date}.jpg'
    ):
        profile_data_json = open_json_file(steamid_profile_json)
    if not(os.path.exists(
        f'date/{steamid}/{steamid}_avatar_{today_date}.jpg'
        ) and os.path.exists(
            f'date/{steamid}/{steamid}_avatarmedium_{today_date}.jpg'
            ) and os.path.exists(
                f'date/{steamid}/{steamid}_avatarfull_{today_date}.jpg'
                )
    ):
        req_profile_info = requests.get(url_profile_info).json()
        write_json_file(req_profile_info, steamid_profile_json)
        profile_data_json = open_json_file(steamid_profile_json)

        p1 = requests.get(img1)
        out1 = open(f"date/{steamid}/{steamid}_avatar_{today_date}.jpg", "wb")
        out1.write(p1.content)
        out1.close()

        p2 = requests.get(img2)
        out2 = open(
            f"date/{steamid}/{steamid}_avatarmedium_{today_date}.jpg",
            "wb")
        out2.write(p2.content)
        out2.close()

        p3 = requests.get(img3)
        out3 = open(
            f"date/{steamid}/{steamid}_avatarfull_{today_date}.jpg",
            "wb")
        out3.write(p3.content)
        out3.close()
    return "Аватар создан!"
