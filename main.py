import datetime
from random import randrange
from typing import Any, Dict, List, Optional, Tuple

import requests
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from database import insert_data_seen_users, insert_data_users, select
from settings import (COUNTRY_ID, ERROR_MESSAGE, GROUP_TOKEN, MAX_CITY_RESULTS,
                      MAX_PHOTOS, MAX_PHOTOS_COUNT, MAX_SEARCH_COUNT,
                      URL_USERS_GET, USER_TOKEN, VK_API_VERSION)


class ChatBotVK:
    def __init__(self):
        self.vk = vk_api.VkApi(token=GROUP_TOKEN)
        self.longpoll = VkLongPoll(self.vk)
        self.url = 'https://api.vk.com/method/'
        print('Bot is running')


    def write_msg(self, user_id: int, message: str) -> None:
        """
        Write a message to the user.

        Args:
            user_id (int): ID of the user to write a message to.
            message (str): Message to send to the user.
        """
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': USER_TOKEN,
                                         'message': message,
                                         'random_id': randrange(10**7)})

    def get_name(self, user_id: int) -> str:
        """
        Getting user name.

        Args:
            user_id (int): ID of the user to get the name of.

        Returns:
            str: First name of the user.
        """
        params = {'access_token': USER_TOKEN,
                  'user_id': user_id,
                  'v': VK_API_VERSION}
        response = requests.get(URL_USERS_GET, params=params).json()
        try:
            info_dict = response['response'][0]
            return info_dict.get('first_name')
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)

    def get_sex(self, user_id: int) -> Optional[int]:
        """
        Getting user sex (replace with opposite).

        Args:
            user_id (int): ID of the user to get the sex of.

        Returns:
            int or None: 1 for female, 2 for male,
            or None if the user's sex is not specified.
        """
        params = {'access_token': USER_TOKEN,
                  'user_id': user_id,
                  'fields': 'sex',
                  'v': VK_API_VERSION}
        response = requests.get(URL_USERS_GET, params=params).json()
        try:
            info_dict = response['response'][0]
            sex = info_dict.get('sex')
            return 2 if sex == 1 else 1 if sex == 2 else None
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)

    def lowest_age(self, user_id: int) -> int:
        """
        Getting the lowest age limit.

        Args:
            user_id (int): ID of the user to get the lowest age limit of.

        Returns:
            int: The lowest age limit.
        """
        params = {'access_token': USER_TOKEN,
                  'user_id': user_id,
                  'fields': 'bdate',
                  'v': VK_API_VERSION}
        response = requests.get(URL_USERS_GET, params=params).json()
        try:
            info_dict = response['response'][0]
            date = info_dict.get('bdate')
            if date:
                year = int(date.split('.')[-1])
                year_now = datetime.date.today().year
                return year_now - year
            else:
                self.write_msg(user_id, 'Enter the lower age threshold (minimum 18):')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return int(age)
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)

    def highest_age(self, user_id: int) -> int:
        """
        Getting the highest age limit.

        Args:
            user_id (int): ID of the user to get the highest age limit of.

        Returns:
            int: The highest age limit.
        """
        params = {'access_token': USER_TOKEN,
                  'user_id': user_id,
                  'fields': 'bdate',
                  'v': VK_API_VERSION}
        response = requests.get(URL_USERS_GET, params=params).json()
        try:
            info_dict = response['response'][0]
            date = info_dict.get('bdate')
            if date:
                year = int(date.split('.')[-1])
                year_now = datetime.date.today().year
                return year_now - year
            else:
                self.write_msg(user_id, 'Enter the upper age threshold (maximum 99): ')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                return int(age)
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)

    def get_city(self, user_id: int, city_name: str) -> Optional[int]:
        """
        Id city by name.

        Args:
            user_id (int): ID of the user to get the city ID for.
            city_name (str): Name of the city to get the ID for.

        Returns:
            int or None: ID of the city, or None if the city was not found.
        """
        url = 'https://api.vk.com/method/database.getCities'
        params = {
            'access_token': USER_TOKEN,
            'country_id': COUNTRY_ID,
            'q': f'{city_name}',
            'need_all': 0,
            'count': MAX_CITY_RESULTS,
            'v': VK_API_VERSION
        }
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            info_list = response['response']['items']
            for city in info_list:
                if city['title'] == city_name:
                    return int(city['id'])
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)

    def find_city_name(self, user_id: int) -> str:
        """
        User's city.

        Args:
            user_id (int): ID of the user to get the city for.

        Returns:
            str: ID of the user's city.
        """
        params = {
            'access_token': USER_TOKEN,
            'fields': 'city',
            'user_ids': user_id,
            'v': VK_API_VERSION
        }
        repl = requests.get(URL_USERS_GET, params=params)
        response = repl.json()
        try:
            info_dict = response['response'][0]
            city = info_dict.get('city')
            if city is not None:
                vk_id = str(city.get('id'))
                return vk_id
            else:
                self.write_msg(user_id, 'Enter your city: ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        city_name = event.text
                        id_city = self.get_city(user_id, city_name)
                        if id_city:
                            return str(id_city)
                        else:
                            break
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)

    def find_pair(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Search for a person matching the parameters.

        Args:
            user_id (int): ID of the user to search for a match for.

        Returns:
            list or None: List of dictionaries representing users matching
            the search parameters, or None if no matches were found.
        """
        url = 'https://api.vk.com/method/users.search'
        params = {
            'access_token': USER_TOKEN,
            'v': VK_API_VERSION,
            'sex': self.get_sex(user_id),
            'age_from': self.lowest_age(user_id),
            'age_to': self.highest_age(user_id),
            'city': self.find_city_name(user_id),
            'fields': 'is_closed, id, first_name, last_name',
            'status': '1' or '6',
            'count': MAX_SEARCH_COUNT
        }
        response = requests.get(url, params=params).json()
        try:
            items = response['response']['items']
            for person in items:
                if not person.get('is_closed'):
                    first_name = person.get('first_name')
                    last_name = person.get('last_name')
                    vk_id = str(person.get('id'))
                    vk_link = f'vk.com/id{vk_id}'
                    insert_data_users(first_name, last_name, vk_id, vk_link)
            return 'Search completed'
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)

    def get_photos_id(self, user_id: int) -> List[Tuple[int, int]]:
        """
        Gets the photo id in reverse order.

        Args:
        - user_id (int): user id

        Returns:
        - List[Tuple[int, int]]: list of tuples,
        containing number of likes and id of photo
        """
        url = 'https://api.vk.com/method/photos.getAll'
        params = {
            'access_token': USER_TOKEN,
            'type': 'album',
            'owner_id': user_id,
            'extended': 1,
            'count': MAX_PHOTOS_COUNT,
            'v': VK_API_VERSION
        }
        repl = requests.get(url, params=params)
        photos = []
        response = repl.json()
        try:
            items = response['response']['items']
            for item in items:
                likes = item['likes'].get('count', 0)
                photo_id = item['id']
                photos.append((likes, photo_id))
            photos.sort(reverse=True)
            return photos
        except KeyError:
            self.write_msg(user_id, ERROR_MESSAGE)

    def send_photos(self, user_id: int, message: str, shift: int) -> None:
        """
        Sends pictures to user.

        Args:
        - user_id (int): user id
        - message (str): message to be sent with the pictures
        - shift (int): offset for user selection

        Returns:
        - None
        """
        photos_list = self.get_photos_id(self.person_id(shift))
        count = min(MAX_PHOTOS, len(photos_list))
        for i in range(count):
            self.vk.method('messages.send', {
                'user_id': user_id,
                'access_token': USER_TOKEN,
                'message': message,
                'attachment': f'photo{self.person_id(shift)}_{photos_list[i][1]}',
                'random_id': 0
            })

    def found_person_info(self, shift: int) -> str:
        """
        Gets information about the user.

        Args:
        - shift (int): offset to select users

        Returns:
        - str: user information
        """
        person_tuple = select(shift)
        return f'{person_tuple[0]} {person_tuple[1]}, ссылка - {person_tuple[3]}'

    def person_id(self, shift: int) -> str:
        """
        Gets the id of the matched user.

        Args:
        - shift (int): offset to select users

        Returns:
        - str: user id as string
        """
        return str(select(shift)[2])

    def find_persons(self, user_id: int, shift: int) -> None:
        """
        Searches for users suitable for communication,
        and sends information and pictures to the user.

        Args:
        - user_id (int): user id
        - shift (int): offset for user selection
        Returns:
        - None
        """
        self.write_msg(user_id, self.found_person_info(shift))
        self.person_id(shift)
        insert_data_seen_users(self.person_id(shift), shift)  # shift
        self.send_photos(user_id, 'Фото номер', shift)


bot = ChatBotVK()
