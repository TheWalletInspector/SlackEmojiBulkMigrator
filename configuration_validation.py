import os
import sys
from enum import Enum
from typing import Dict

from pydantic import BaseModel, validator

_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(_FILE_PATH)))
sys.path.append(os.path.join(_ROOT_DIR, "python_modules"))

from exceptions import MissingEnvironment


class Environments(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"


class Credentials(BaseModel):
    username: str
    password: str


class APIConfiguration(BaseModel):
    public_key: str = ""
    private_key_enc: str = ""
    credentials: Dict[Environments, Credentials]

    # pylint: disable=E0213
    @validator("credentials", pre=True, always=True)
    def check_credentials(cls, credentials):
        missing_environments = {"staging", "production"} - set(credentials.keys())
        if missing_environments:
            raise MissingEnvironment(missing_environments)
        return credentials
