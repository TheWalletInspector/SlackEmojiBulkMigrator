import pytest
from mockito import unstub


@pytest.fixture(scope="session")
def mockito_handler():
    print("mockito setup")
    yield
    print("mockito teardown")
    unstub()
