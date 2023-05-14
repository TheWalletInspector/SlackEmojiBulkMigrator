import logging

# from backoff import on_exception, expo
# from ratelimit import limits, RateLimitException
import string

import requests
import aiohttp
import re
import asyncio
from slack_sdk import WebClient
from collections import namedtuple
from time import sleep

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s\t%(message)s")
logger = logging.getLogger(__name__)

BASE_URL = 'https://{team_name}.slack.com'
EMOJI_ENDPOINT = '/customize/emoji'
EMOJI_API_LIST = '/api/emoji.adminList'

_URL_CUSTOMIZE = "https://beyondtheenva-coh7175.slack.com/customize/emoji"
_URL_ADD = "https://beyondtheenva-coh7175.slack.com/api/emoji.add"
_URL_LIST = "https://beyondtheenva-coh7175.slack.com/api/emoji.adminList"

from dataclasses import dataclass


@dataclass
class Emoji:
    url: string
    name: string
    extension: string


@dataclass
class Config:
    verify_ssl: bool = True
    tcp_connections: int = 5


class SlackHttpHandler:
    def __init__(self, auth_cookie: str, config: Config = None) -> None:
        self.auth_cookie = auth_cookie
        self.config = Config() if config is None else config
        assert isinstance(self.config, Config)

    async def __aenter__(self):
        self._conn = aiohttp.TCPConnector(
            verify_ssl=self.config.verify_ssl, limit=self.config.tcp_connections
        )
        self._session = aiohttp.ClientSession(headers={"Cookie": self.auth_cookie})
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()
        await self._conn.close()

    @staticmethod
    async def get_remote_emoji_list(session: aiohttp.ClientSession, base_url: str, token: str):
        page = 1
        total_pages = None
        filtered_entries = list()

        while total_pages is None or page <= total_pages:
            data = {
                'token': token,
                'page': page,
                'limit_per_page': 100
            }
            response = await session.post(base_url + EMOJI_API_LIST, data=data)

            logger.info(f"loaded {response.real_url} (page {page})")

            if response.status != 200:
                raise Exception(
                    f"Failed to load emoji from {response.request_info.real_url} (status {response.status})")

            json_response = await response.json()

            for entry in json_response['emoji']:
                url = str(entry['url'])
                # url = json_response[entry]
                name = str(entry['name'])
                # name = str(entry)
                extension = str(url.split('.')[-1])
                # extension = re.search('\.\w+$', url).group()

                # slack uses 0/1 to represent false/true in the API
                if url.startswith('alias:'):
                    logger.info(f"Skipping emoji \"{name}\", is alias of \"{entry['alias_for']}\"")
                    continue

                filtered_entries.append(Emoji(url, name, extension))

            if total_pages is None:
                total_pages = int(json_response['paging']['pages'])

            page += 1

        return filtered_entries

    @staticmethod
    def upload_emoji(emoji_name, file_url):
        destinationSlackOrgToken = ''
        destinationSlackOrgCookie = ''
        headers = {'cookie': destinationSlackOrgCookie,
                   'Authorization': f'Bearer {destinationSlackOrgToken}'}
        url = 'https://slack.com/api/emoji.add'
        data = {
            'mode': 'data',
            'name': emoji_name,
        }

    # def upload_emoji(self, session, emoji_name, filename):
    def upload_emoji(self, emoji_name, url):
        session = requests.session()
        session.headers = {
            'Cookie': ''}
        session.url_customize = URL_CUSTOMIZE
        session.url_add = URL_ADD
        session.url_list = URL_LIST
        session.api_token = ''

        data = {
            'mode': 'data',
            'name': emoji_name,
            'token': session.api_token
        }

        while True:
            with open(url, 'rb') as f:
                files = {'image': f}
                response = session.post(url=session.url_add, data=data, files=files, allow_redirects=False)

                if response.status_code == 429:
                    wait = int(response.headers.get('retry-after', 1))
                    print("429 Too Many Requests!, sleeping for %d seconds" % wait)
                    sleep(wait)
                    continue

            response.raise_for_status()

            # Slack returns 200 OK even if upload fails, so check for status.
            json_response = response.json()
            if not json_response['ok']:
                print("Error with uploading %s: %s" % (emoji_name, json_response))
            break

    @staticmethod
    def get_emoji(url):
        try:
            response = requests.get(url)
            response.raise_for_status()

        except requests.exceptions.RequestException as err:
            logger.error(f"API call failed with exception: {err}")
            raise err

        return response.content
