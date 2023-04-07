import asyncio
import logging
import os
import re
from collections import namedtuple
from emoji_bulk_migrator.slack_web_api_handler import SlackWebApiHandler
from emoji_bulk_migrator.slack_http_handler import SlackHttpHandler
from emoji_bulk_migrator.local_file_handler import LocalFileHandler

# _CONFIG_PATH = '../config/'
# _CONFIG = 'api_configuration'
_FILE_COUNT = namedtuple('FileCount', 'processed skipped')

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s\t%(message)s")
logger = logging.getLogger(__name__)


async def main(path, api_protocol, download, upload):
    """Runs the Emoji Migrator APP

    Parameters
    ----------
    path : str
        The local file path where emojis will be stored for downloading and uploading
    api_protocol: str
        The type of web protocol to be used. If you are not a slack admin, using the api protocol is not possible.
    download : str
        Flag to tell app to download emojis from source API.
    upload : str
        Flag to tell app to upload emojis from source API.

    """

    http_cookie_token = ''
    slack_web_token = ''

    file_handler = LocalFileHandler(path)

    match api_protocol:
        case 'http':
            api_handler = SlackHttpHandler(token=http_cookie_token)
        case 'slack_web':
            api_handler = SlackWebApiHandler(token=slack_web_token)
        case _:
            raise Exception('No match found')

    if download:
        files_count = _download_files(file_handler, api_handler)
        logger.info(f"Downloaded {files_count.processed} new emojis.")
        logger.info(f"Skipped {files_count.skipped} existing emojis.")

    if upload:
        files_count = _upload_files(file_handler, api_handler)
        logger.info(f"Uploaded {files_count.processed} new emojis.")
        logger.info(f"Skipped {files_count.skipped} existing emojis.")

    logger.info("Emoji migration complete.")


def _download_files(file_handler: LocalFileHandler, api_handler):
    existing_local_files = file_handler.get_existing_local_files()
    existing_remote_files = api_handler.get_remote_emoji_list()

    files_processed = 0
    files_skipped = 0
    _FILE_COUNT(0, 0)

    for file in existing_remote_files:
        filename = f'{file.name}{file.extension}'

        invalid_filename_characters: str = ':|;'
        cleansed_remote_file = re.sub(invalid_filename_characters, '_', filename)

        if cleansed_remote_file in existing_local_files:
            logger.info(f"File already exists locally. Skipping emoji \"{file.name}\"")
            files_skipped += 1
            continue

        emoji_content = api_handler.get_emoji(file.url)
        file_handler.write_local_file(filename, emoji_content)

        files_processed += 1
    return _FILE_COUNT(files_processed, files_skipped)


def _upload_files(path, file_handler, api_handler):
    existing_local_files = file_handler.get_existing_local_files()
    existing_remote_files = api_handler.get_remote_files_list()

    files_processed = 0
    files_skipped = 0
    _FILE_COUNT(0, 0)

    remote_filenames = [f'{file.name}{file.extension}' for file in existing_remote_files]

    for local_filename in existing_local_files:
        file_url = f'{path}/{local_filename}'

        if local_filename in remote_filenames:
            logger.info(f"File already exists remotely. Skipping emoji \"{local_filename}\"")
            files_skipped += 1
            continue

        api_handler.upload_emoji(emoji_name=local_filename, url=file_url)
        logger.info(f"File uploaded to: {file_url}")
        files_processed += 1
    return _FILE_COUNT(files_processed, files_skipped)
