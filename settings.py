import os

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DB_NAME = os.getenv('DB_NAME')

USER_TOKEN = os.getenv('USER_TOKEN')
GROUP_TOKEN = os.getenv('GROUP_TOKEN')

SHIFT = 0
LINE = range(0, 1000)

VK_API_VERSION = '5.131'
MAX_CITY_RESULTS = 1000
COUNTRY_ID = 1

MAX_PHOTOS_COUNT = 25
MAX_PHOTOS = 3  # Maximum number of photos to send
MAX_SEARCH_COUNT = 500

URL_USERS_GET = 'https://api.vk.com/method/users.get'
ERROR_MESSAGE = 'Error, not enough data, enter token in USER_TOKEN'
