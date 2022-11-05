import logging
import os
from os import walk

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s\t%(message)s")
logger = logging.getLogger(__name__)


class LocalFileHandler:
    def __init__(self, path):
        self._path = path

    def write_local_file(self, filename, file_content):
        self._make_dir()
        with open(f'{self._path}/{filename}', 'wb') as file:
            file.write(file_content)
        logger.info(f"File saved to: {self._path}/{filename}")

    def _make_dir(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def get_existing_local_files(self):
        existing_files = []
        for (dirpath, dirnames, filenames) in walk(self._path):
            existing_files.extend(filenames)
            break
        return existing_files
