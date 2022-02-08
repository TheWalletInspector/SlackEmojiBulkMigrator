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


source_token = os.environ["SOURCE_SLACK_API_TOKEN"]

print( DownloadEmoji(source_token, 'emoji').run())

dest_cookie = os.environ["SOURCE_SLACK_COOKIE"]
dest_token = os.environ["SOURCE_SLACK_TOKEN"]


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
