import logging
import re

# from backoff import on_exception, expo
# from ratelimit import limits, RateLimitException
import requests
from slack_sdk import WebClient
from collections import namedtuple
from time import sleep

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s\t%(message)s")
logger = logging.getLogger(__name__)

URL_CUSTOMIZE = "https://beyondtheenva-coh7175.slack.com/customize/emoji"
URL_ADD = "https://beyondtheenva-coh7175.slack.com/api/emoji.add"
URL_LIST = "https://beyondtheenva-coh7175.slack.com/api/emoji.adminList"
_EMOJI = namedtuple('Emoji', 'url name extension')


class SlackWebApiHandler:
    def __init__(self, **kwargs):
        self._token = kwargs['token']
        self._api_client = self._create_api_client(self._token)

    def get_and_filter_remote_emoji_list(self):
        emoji_list_response = self._get_remote_emoji_list()
        emoji_dict = emoji_list_response.get("emoji")
        filtered_emoji_records = []

        for key in emoji_dict:
            url = emoji_dict[key]
            if url.startswith('alias:'):
                continue
            name = str(key)
            extension = re.search('\.\w+$', url).group()
            filtered_emoji_records.append(_EMOJI(url, name, extension))
        return filtered_emoji_records

    def _get_remote_emoji_list(self):
        try:
            response = self._api_client.emoji_list()
            return response.data
        except Exception as err:
            logger.error(f"API call failed with exception: {err}")
            raise err

    def upload_emoji(self, file_name, url):
        try:
            return self._api_client.admin_emoji_add(name=file_name, url=url)
        except Exception as err:
            logger.error(f"API call failed with exception: {err}")
            raise err

    @staticmethod
    def get_emoji(url):
        try:
            response = requests.get(url)
            response.raise_for_status()

        except requests.exceptions.RequestException as err:
            logger.error(f"API call failed with exception: {err}")
            raise err

        return response.content

    @staticmethod
    def _create_api_client(_token):
        return WebClient(token=_token)
