import pytest
import requests
from mockito import when, mock
from emoji_bulk_migrator.slack_http_handler import SlackHttpHandler


def test__get_remote_emoji_list__returns_entries_list_from_payload(mockito_handler):
    pass


def test__get_remote_emoji_list__returns_two_pages_of_entries_from_large_payload(mockito_handler):
    pass


def test__get_remote_emoji_list__skips_aliases(mockito_handler):
    pass


def test__upload_emoji__successfully_uploads_a_file_from_local_directory(mockito_handler):
    pass
