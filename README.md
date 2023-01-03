Emoji Upload/Download scripts

This python app te enable bulk uploading and dowmloading of emojis from any Slack workspace. It is currently set to use local storage as the intermeidiary.

### NOTE: This script will only work if you have access to see the emoji page for your source slack org and access to add custom emoji in your destination slack org and you have an app with an API token that allows that access.

### Dependencies

1. [Python 3](https://www.python.org/downloads/)
1. Requests pip3 library.  To install run `pip3 install requests` in a command prompt after installing Python.


### Running Instructions

#### Download

* Set your api token in `SOURCE_SLACK_API_TOKEN` in your environment.


## Notes

The script will not download emoji you have already downloaded and will not try upload emoji you have already uploaded so if you run into an error that causes the script to fail you can restart it and it will pick up where it left off.

Inspired by https://github.com/Firenza/ExportImportSlackEmoji and initial forked from that repo, but then I made a pile of changes.
