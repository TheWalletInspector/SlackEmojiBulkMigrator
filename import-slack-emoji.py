import sys
import argparse
import requests
import json
import re
import os
import time
import re
from os import walk


def construct_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }

class SourceClient:
    def __init__(self, token, path):
        self.token = token
        self.path = path

    def download_emoji(self, url, fname):
        response = requests.get(url)

        invalidFileNameCharatersRegex = ':|;'
        filename = re.sub(invalidFileNameCharatersRegex, '_', fname)
        open(filename, 'wb').write(response.content)
        pass

    @property
    def headers(self):
        return construct_headers(self.token)

    def get_emojis(self, url):
        url = 'https://slack.com/api/emoji.list'
        response = requests.get(url, headers=self.headers)
        return json.loads(response.content)


class DownloadEmoji:
    def __init__(self, token, path):
        self.token = token
        self.path = path

    @property
    def client(self):
        return SourceClient(self.token, self.path)

    def current_emojis(self):
        response = self.client.get_emojis('https://slack.com/api/emoji.list')
        return response.get("emoji", {})

    def makeDir(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def find_existing(self):
        existing_files = []
        for (dirpath, dirnames, filenames) in walk(self.path):
            existing_files.extend(filenames)
            break
        return existing_files

    def _download(self, skip_list):
        existing = self.find_existing()
        available = self.current_emojis()

        for name in available:
            url = available[name]
            if url.startswith('alias:'):
                continue

            ext = re.search('\.\w+$', url).group()

            fname = f'{name}{ext}'
            if fname in existing:
                # emoji already downloaded
                continue
            print(f"Downloading {self.path}/{fname}")

            self.client.download_emoji(url, f'{self.path}/{fname}')

    def run(self):
        self.makeDir()
        existing_files = self.find_existing()
        self._download(existing_files)


parser = argparse.ArgumentParser(description="Download emojis from Slack")
parser.add_argument('-p', '--path', default="emojis", help="path to put emojis")

args = parser.parse_args()

try:
    source_token = os.environ["SOURCE_SLACK_API_TOKEN"]
    DownloadEmoji(source_token, args.path).run()
except:
    print("You must choose (at a minimum) import or export (-i or -e)")
    print("And don't forget to set SOURCE_SLACK_API_TOKEN in your environment")
    parser.print_help()
