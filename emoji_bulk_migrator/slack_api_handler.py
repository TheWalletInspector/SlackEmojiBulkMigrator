import logging

from backoff import on_exception, expo
from ratelimit import limits, RateLimitException
import requests
from slack_sdk import WebClient
from time import sleep

LOGGER = logging.getLogger(__name__)

URL_CUSTOMIZE = "https://beyondtheenva-coh7175.slack.com/customize/emoji"
URL_ADD = "https://beyondtheenva-coh7175.slack.com/api/emoji.add"
URL_LIST = "https://beyondtheenva-coh7175.slack.com/api/emoji.adminList"


class SlackApiHandler:
    def __init__(self, **kwargs):
        self._token = kwargs['token']
        self._api_client = SlackApiHandler._create_api_client(self._token)

    def get_emoji_list(self):
        try:
            response = self._api_client.emoji_list()
            return response.data
        except Exception as err:
            LOGGER.error(f"API call failed with exception: {err}")
            raise err

    def load_emoji(self, file_name, url):
        try:
            return self._api_client.admin_emoji_add(name=file_name, url=url)
        except Exception as err:
            LOGGER.error(f"API call failed with exception: {err}")
            raise err

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
