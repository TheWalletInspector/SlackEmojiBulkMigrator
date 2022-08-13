import logging
import os
import sys

from python_api_ingestion_template.api_handler import ApiHandler
from python_api_ingestion_template.configuration_validation import APIConfiguration

_CONFIG_PATH = './config/'
_CONFIG = 'api_configuration'


def main(configuration=_CONFIG, path=_CONFIG_PATH):
    """Runs the ingestion APP

    Parameters
    ----------
    configuration : str
        The name of the configuration to be used when the application runs
    path : str
        The pipeline configuration path

    Raises
    ------
    PIIRedactionNeeded
        Indicates that the data being extracted contains PII that requires redacting
    """
    application_config = decrypt_application_configuration(
        config_path=path,
        pydantic_model=APIConfiguration,
        folder="pythonapiingestiontemplate",
        file_name=f"{configuration}.ejson"
    )

    api_handler = ApiHandler(application_config)

    logging.getLogger(__name__).info(
        f"Requesting the {configuration} for the execution date {execution_date}."
    )
    bucket_path = "template_api_ingestion"
    record_count = api_handler.get_resource(
        execution_date=execution_date,
        write_function=lambda data, batch_number: data_lake.write(
            f"{bucket_path}/{configuration}",
            to_jsonl(data),
            lambda: f"{downloaded_at()}_{batch_number}.jsonl"
        )
    )
    logging.getLogger(__name__).info(f"Written {record_count} new records.")
