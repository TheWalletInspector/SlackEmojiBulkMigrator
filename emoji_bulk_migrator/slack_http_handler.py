import logging

from backoff import on_exception, expo
from ratelimit import limits, RateLimitException
import requests
import aiohttp
import asyncio
from slack_sdk import WebClient
from time import sleep

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s\t%(message)s")
logger = logging.getLogger(__name__)

BASE_URL = 'https://{team_name}.slack.com'
EMOJI_ENDPOINT = '/customize/emoji'
EMOJI_API_LIST = '/api/emoji.adminList'

URL_CUSTOMIZE = "https://beyondtheenva-coh7175.slack.com/customize/emoji"
URL_ADD = "https://beyondtheenva-coh7175.slack.com/api/emoji.add"
URL_LIST = "https://beyondtheenva-coh7175.slack.com/api/emoji.adminList"


class SlackHttpHandler:
    def __init__(self, **kwargs):
        self._token = kwargs['token']
        self._api_client = SlackHttpHandler._create_api_client(self._token)


    def get_remote_emoji_list(self):
        emoji_list_response = self._get_emoji_list(session= , base_url=, token=self._token)
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

    async def _get_emoji_list(self, session: aiohttp.ClientSession, base_url: str, token: str):
        page = 1
        total_pages = None

        entries = list()

        while total_pages is None or page <= total_pages:
            data = {
                'token': token,
                'page': page,
                'count': 100
            }
            response = await session.post(base_url + EMOJI_API_LIST, data=data)

            logger.info(f"loaded {response.real_url} (page {page})")

            if response.status != 200:
                raise Exception(
                    f"Failed to load emoji from {response.request_info.real_url} (status {response.status})")

            json = await response.json()

            for entry in json['emoji']:
                url = str(entry['url'])
                name = str(entry['name'])
                extension = str(url.split('.')[-1])

                # slack uses 0/1 to represent false/true in the API
                if entry['is_alias'] != 0:
                    logger.info(f"Skipping emoji \"{name}\", is alias of \"{entry['alias_for']}\"")
                    continue

                entries.append(Emoji(url, name, extension))

            if total_pages is None:
                total_pages = int(json['paging']['pages'])

            page += 1

        return entries

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
                resp = session.post(session.url_add, data=data, files=files, allow_redirects=False)

                if resp.status_code == 429:
                    wait = int(resp.headers.get('retry-after', 1))
                    print("429 Too Many Requests!, sleeping for %d seconds" % wait)
                    sleep(wait)
                    continue

            resp.raise_for_status()

            # Slack returns 200 OK even if upload fails, so check for status.
            response_json = resp.json()
            if not response_json['ok']:
                print("Error with uploading %s: %s" % (emoji_name, response_json))

            break

    @staticmethod
    def get_emoji(url):
        try:
            response = requests.get(url)
            response.raise_for_status()

        except requests.exceptions.RequestException as err:
            LOGGER.error(f"API call failed with exception: {err}")
            raise err

        return response.content

    @staticmethod
    def _create_api_client(_token):
        return WebClient(token=_token)
