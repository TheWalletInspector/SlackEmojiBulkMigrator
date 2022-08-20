import argparse
import logging
import sys
import os
from emoji_bulk_migrator import main

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M"
)

parser = argparse.ArgumentParser(
    description="This text should be changed for each application. Template application for ingesting from and Api source and into the the datalake."
)
parser.add_argument(
    "-d",
    "--download",
    action=argparse.BooleanOptionalAction,
    required=False,
    help="The flag to download the emojis from the api source to the path directory.",
)
parser.add_argument(
    "-u",
    "--upload",
    action=argparse.BooleanOptionalAction,
    required=False,
    help="The flag to upload the files in the path directory to the api destination.",
)
parser.add_argument(
    "-p",
    "--path",
    type=str,
    required=False,
    default="./emojis",
    help="The local directory where emojis will be downloaded to and uploaded from.",
)
args = parser.parse_args()

try:
    main(path=args.path, download=args.download, upload=args.upload)
except Exception as cause:
    logging.getLogger(__name__).error(
        f"{os.path.basename(os.path.dirname(sys.argv[0]))} when running: failed with exception", exc_info=True)
    raise cause
