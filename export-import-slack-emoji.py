#!/usr/bin/env python3

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

class SlackEmojiClient:
    def __init__(self, token, path):
        self.token = token
        self.path = path

    @property
    def _headers(self):
        return construct_headers(self.token)

    def download(self, url, fname):
        response = requests.get(url)

        invalidFileNameCharatersRegex = ':|;'
        filename = re.sub(invalidFileNameCharatersRegex, '_', fname)
        open(filename, 'wb').write(response.content)
        pass

    def upload(self, fname):
        url = 'https://slack.com/api/emoji.add'
        response = requests.get(url, headers=self._headers)
        return json.loads(response.content)


    def list(self, url):
        url = 'https://slack.com/api/emoji.list'
        response = requests.get(url, headers=self._headers)
        return json.loads(response.content)


class BaseEmojiService:
    def __init__(self, token, path):
        self.token = token
        self.path = path

    @property
    def client(self):
        return SlackEmojiClient(self.token, self.path)

    def current_emojis(self):
        response = self.client.list('https://slack.com/api/emoji.list')
        return response.get("emoji", {})

    def find_downloaded(self):
        existing_files = []
        for (dirpath, dirnames, filenames) in walk(self.path):
            existing_files.extend(filenames)
            break
        return existing_files

class DownloadEmoji(BaseEmojiService):
    def makeDir(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)


    def _download(self, skip_list):
        existing = self.find_downloaded()
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

            self.client.download(url, f'{self.path}/{fname}')

    def run(self):
        self.makeDir()
        existing_files = self.find_existing()
        self._download(existing_files)


class UploadEmoji(BaseEmojiService):

    def run(self):
        existing = self.current_emojis()
        files = self.find_downloaded()
        for fname in files:
            basename = ext = re.search('([^\.]+)\.', fname).group(1)
            print(basename, ext)
            if basename in existing:
                print(f"Skipping - {basename} already exists")
                continue
            else:
                pass

# destinationEmojiNameToUrlDict = getEmojiNameToUrlDict(destinationSlackOrgHeaders)

# url = 'https://slack.com/api/emoji.add'
# emojiNum = 0

# for emojiFileName in existingEmojiFileNames:

#     emojiFileNameWithoutExtension = emojiFileExtension = re.search('([^\.]+)\.', emojiFileName).group(1)

#     if emojiFileNameWithoutExtension in destinationEmojiNameToUrlDict:
#         print(f'Emoji with a name of {emojiFileNameWithoutExtension} already exits in destination, skipping upload')
#         continue

#     emojiUploaded = False

#     while (not emojiUploaded):

#         payload = {
#             'mode': 'data',
#             'name': emojiFileNameWithoutExtension
#         }

#         files = [
#             ('image', open(f'slackEmoji/{emojiFileName}','rb'))
#         ]

#         response = requests.request("POST", url, headers=destinationSlackOrgHeaders, data = payload, files = files)

#         responseJson = json.loads(response.content)

#         if responseJson["ok"]:
#             print(f'Uploaded {emojiFileName}')
#             emojiUploaded = True
#         elif not responseJson["ok"] and responseJson["error"] == "error_name_taken":
#             print(f'Emoji with a name of {emojiFileNameWithoutExtension} already exits')
#             emojiUploaded = True
#         elif not responseJson["ok"] and responseJson["error"] == "ratelimited":
#             retryAfter = response.headers['retry-after']
#             retryAfterInt = int(retryAfter) + 1
#             print(f'Exceeded rate limit, waiting {retryAfterInt} seconds before retrying')
#             time.sleep(retryAfterInt)
#         else:
#             print(f'Unexpected failure! {responseJson["error"]}')
#             print(response)
#             print(response.headers)
#             break


token = os.environ["SOURCE_SLACK_API_TOKEN"]

# print( DownloadEmoji(token, 'emoji').run())
print( UploadEmoji(token, 'emoji').run())


# for emojiName in emojiNameToUrlDict:

#     emojiUrl = emojiNameToUrlDict[emojiName]
#     if not emojiUrl.startswith('alias:'):

#         emojiFileExtension = re.search('\.\w+$', emojiUrl).group()

#         emojiFileName = f'{emojiName}{emojiFileExtension}'

#         if emojiFileName in existingEmojiFileNames:
#             print(f'Emoji {emojiName}{emojiFileExtension} already downloaded, skipping download')
#             continue

#         response = requests.get(emojiUrl)

#         # Write the resposne to a file
#         invalidFileNameCharatersRegex = ':|;'
#         emojiFileName = f'{emojiDownloadFolder}/{emojiName}{emojiFileExtension}'
#         emojiFileName = re.sub(invalidFileNameCharatersRegex, '_', emojiFileName)
#         open(emojiFileName, 'wb').write(response.content)

#         print(f'Saved {emojiFileName}')

# ----------------
# Do the uploading
# ----------------

# get the existing emoji so we scan skip trying to upload any already existing emoji
# destinationEmojiNameToUrlDict = getEmojiNameToUrlDict(destinationSlackOrgHeaders)

# url = 'https://slack.com/api/emoji.add'
# emojiNum = 0

# for emojiFileName in existingEmojiFileNames:

#     emojiFileNameWithoutExtension = emojiFileExtension = re.search('([^\.]+)\.', emojiFileName).group(1)

#     if emojiFileNameWithoutExtension in destinationEmojiNameToUrlDict:
#         print(f'Emoji with a name of {emojiFileNameWithoutExtension} already exits in destination, skipping upload')
#         continue

#     emojiUploaded = False

#     while (not emojiUploaded):

#         payload = {
#             'mode': 'data',
#             'name': emojiFileNameWithoutExtension
#         }

#         files = [
#             ('image', open(f'slackEmoji/{emojiFileName}','rb'))
#         ]

#         response = requests.request("POST", url, headers=destinationSlackOrgHeaders, data = payload, files = files)

#         responseJson = json.loads(response.content)

#         if responseJson["ok"]:
#             print(f'Uploaded {emojiFileName}')
#             emojiUploaded = True
#         elif not responseJson["ok"] and responseJson["error"] == "error_name_taken":
#             print(f'Emoji with a name of {emojiFileNameWithoutExtension} already exits')
#             emojiUploaded = True
#         elif not responseJson["ok"] and responseJson["error"] == "ratelimited":
#             retryAfter = response.headers['retry-after']
#             retryAfterInt = int(retryAfter) + 1
#             print(f'Exceeded rate limit, waiting {retryAfterInt} seconds before retrying')
#             time.sleep(retryAfterInt)
#         else:
#             print(f'Unexpected failure! {responseJson["error"]}')
#             print(response)
#             print(response.headers)
#             break
