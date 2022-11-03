import logging
import os
import re
from os import walk
from collections import namedtuple
from emoji_bulk_migrator import slack_api_handler

_CONFIG_PATH = '../config/'
_CONFIG = 'api_configuration'

_FILE_COUNT = namedtuple('FileCount', 'processed skipped')
LOGGER = logging.getLogger(__name__)


def main(path, protocol, download, upload):
    """Runs the Emoji Migrator APP

    Parameters
    ----------
    configuration : str
        The name of the configuration to be used when the application runs
    path : str
        The pipeline configuration path
    download : str
        Flag to tell app to download emojis from source API.
    upload : str
        Flag to tell app to upload emojis from source API.

    """

    source_token = ''
    destination_token = ''

    match protocol:
        case 'http':
            print('Hello to you too!')
        case 'api':
            api_handler = slack_api_handler.SlackApiHandler(token=source_token)
        case other:
            print('No match found')

    if download:

        files_count = _download_files(api_handler, path)
        LOGGER.info(f"Downloaded {files_count.processed} new emojis.")
        LOGGER.info(f"Skipped {files_count.skipped} existing emojis.")

    if upload:
        api_handler = slack_api_handler.SlackApiHandler(token=destination_token)
        files_count = _upload_files(api_handler, path)
        LOGGER.info(f"Uploaded {files_count.processed} new emojis.")
        LOGGER.info(f"Skipped {files_count.skipped} existing emojis.")

    LOGGER.info("Emoji migration complete.")


def _download_files(api_handler, path):
    existing_local_files = _get_existing_local_files(path)
    existing_remote_files = api_handler.get_remote_emoji_list()

    files_processed = 0
    files_skipped = 0
    _FILE_COUNT(0, 0)
    for file in existing_remote_files:
        filename = f'{file.name}{file.extension}'
        invalid_filename_characters: str = ':|;'
        cleansed_filename = re.sub(invalid_filename_characters, '_', filename)

        if cleansed_filename in existing_local_files:
            files_skipped += 1
            continue

        emoji_content = api_handler.get_emoji(file.url)
        _write_local_file(path, filename, emoji_content)

        files_processed += 1
    return _FILE_COUNT(files_processed, files_skipped)


def _upload_files(api_handler, path):
    existing_local_files = _get_existing_local_files(path)
    existing_remote_files = get_remote_files_list()
    remote_filename = [f'{file.name}{file.extension}' for file in existing_remote_files]

    files_processed = 0
    files_skipped = 0
    _FILE_COUNT(0, 0)
    for local_file in existing_local_files:
        file_url = f'{path}/{local_file}'

        if local_file in remote_filename:
            files_skipped += 1
            continue

        # api_handler.load_emoji(file_name=local_file, url=file_url)
        api_handler.upload_emoji(emoji_name=local_file, url=file_url)
        LOGGER.info(f"File uploaded to: {file_url}")
        files_processed += 1
    return _FILE_COUNT(files_processed, files_skipped)


def _write_local_file(path, filename, file_content):
    _make_dir(path)
    with open(f'{path}/{filename}', 'wb') as file:
        file.write(file_content)
    LOGGER.info(f"File downloaded to: {path}/{filename}")


def _get_existing_local_files(path):
    existing_files = []
    for (dirpath, dirnames, filenames) in walk(path):
        existing_files.extend(filenames)
        break
    return existing_files


def _make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
