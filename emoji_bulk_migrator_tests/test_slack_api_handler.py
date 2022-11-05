import pytest
import requests
from mockito import unstub, when, mock
from emoji_bulk_migrator.slack_web_api_handler import SlackApiHandler


class TestSlackApiHandler:
    def teardown(self):
        unstub()

    def test__get_emoji_with_successful(self):
        mocked_response = mock({'content': 'Ok'}, spec=requests.Response)
        when(requests).get(...).thenReturn(mocked_response)
        when(mocked_response).raise_for_status()

        api_handler = SlackApiHandler(workspace="workspace", token="token")
        response = api_handler.get_emoji("url")

        assert response == "Ok"

    def test__get_emoji_with_not_successful(self):
        mocked_response = mock({'content': 'Ok'}, spec=requests.Response)
        when(requests).get(...).thenReturn(mocked_response)
        when(mocked_response).raise_for_status().thenRaise(requests.exceptions.RequestException)

        api_handler = SlackApiHandler(workspace="workspace", token="token")

        with pytest.raises(requests.exceptions.RequestException):
            api_handler.get_emoji("url")
