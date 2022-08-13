import json
import sys
import base64
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M"
)

# make sure the output directory exists before running!
folder = os.path.join(os.getcwd(), "emojis")

with open("../envato_slack_com.har", "r") as f:
    har = json.loads(f.read())

entries = har["log"]["entries"]

for entry in entries:
    if entry["_resourceType"] == 'image' and entry["request"]["url"].split("/")[3] == 'T0253B9P9':
        mimetype = entry["response"]["content"]["mimeType"]
        filename = entry["request"]["url"].split("/")[4]
        filename = filename[:50]
        print(filename)
        print(entry["request"]["url"])
        print(entry["request"]["url"].split("/")[3])
        try:
            image64 = entry["response"]["content"]["text"]

            if any([
                mimetype == "image/webp",
                mimetype == "image/jpeg",
                mimetype == "image/png",
                mimetype == "image/gif"
            ]):
                ext = {
                    "image/webp": "webp",
                    "image/jpeg": "jpg",
                    "image/png": "png",
                    "image/gif": "gif"
                }.get(mimetype)
                file = os.path.join(folder, f"{filename}.{ext}")
                print(file)
                with open(file, "wb") as f:
                    f.write(base64.b64decode(image64))
        except Exception as cause:
            logging.getLogger(__name__).error(
                f"{os.path.basename(os.path.dirname(sys.argv[0]))} when running: failed with exception", exc_info=True)
            continue
            # raise cause

