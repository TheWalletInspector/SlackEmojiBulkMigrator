import pytest
import requests
from mockito import when, mock
from emoji_bulk_migrator.slack_web_api_handler import SlackWebApiHandler


def test__get_emoji__with_successful_api_response(mockito_handler):
    mocked_response = mock({'content': 'Ok'}, spec=requests.Response)
    when(requests).get(...).thenReturn(mocked_response)
    when(mocked_response).raise_for_status()

    api_handler = SlackWebApiHandler(workspace="workspace", token="token")
    response = api_handler.get_emoji("url")

    assert response == "Ok"


def test__get_emoji__with_not_successful_api_response(mockito_handler):
    mocked_response = mock({'content': 'Ok'}, spec=requests.Response)
    when(requests).get(...).thenReturn(mocked_response)
    when(mocked_response).raise_for_status().thenRaise(requests.exceptions.RequestException)

    api_handler = SlackWebApiHandler(workspace="workspace", token="token")

    with pytest.raises(requests.exceptions.RequestException):
        api_handler.get_emoji("url")
