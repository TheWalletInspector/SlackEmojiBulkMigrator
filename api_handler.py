import logging

from backoff import on_exception, expo
from ratelimit import limits, RateLimitException

LOGGER = logging.getLogger(__name__)


class ApiHandler:
    def __init__(self, api_config):
        self._api_client = ApiHandler._create_api_client(api_config)

    # pylint: disable=W0511
    # TODO It may be required to add additional params here depending on the api
    # TODO Please read ADR relating to back off handling and rate limits to determine what is suitable for this api.
    # pylint: enable=W0511
    @on_exception(expo, RateLimitException, max_tries=3, jitter=None, factor=60)
    @limits(calls=15, period=120)
    # pylint: disable=W0613
    def get_resource(self, execution_date, write_function):
        batch_number = 0
        data = self._api_client.invoke_endpoint(execution_date)
        # Invoke self._api_client to get response data.
        # Any page handling should be handled here if required.
        # Using the write function you can write each page/batch in its own file using a batch number to distinguish.
        # Data should be collection of records returned from the api.
        write_function(data, batch_number)
        logging.getLogger(__name__).info(f"Writing batch {batch_number}.")
        return len(data)

    # pylint: enable=W0613

    # pylint: disable=W0613
    @staticmethod
    def _create_api_client(api_config):
        # pylint: disable=W0511
        # TODO: Implement this method to establish a connection to the underlying api client using api_config.
        #  This method should return a reference to the client.
        # pylint: enable=W0511
        return None
    # pylint: enable=W0613
