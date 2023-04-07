import emoji_bulk_migrator
from emoji_bulk_migrator import main, _download_files, _upload_files
from mockito import mock, unstub, verify, when, expect

API_CONFIG = {
    "public_key": "c12695023k45j23k4hvk2hg",
    "private_key_enc": "decrypted_private_key",
    "local_directory": "local/directory/where/emojis/are/downloaded",
    "credentials": {
        "source": {
            "workspace": "source_workspace>",
            "token": "source_token"
        },
        "destination": {
            "workspace": "destination_workspace",
            "token": "destination_token"
        }
    }
}

existing_remote_files = {
    "ok": "true",
    "emoji": {
        "bowtie": "https://emoji.slack-edge.com/account_id/bowtie/f3ec6f2bb0.png",
        "squirrel": "https://emoji.slack-edge.com/account_id/squirrel/465f40c0e0.jpg",
        "shipit": "alias:squirrel"
    }
}

api_handler = mock()
mock_emoji = mock()


class TestMain:
    def teardown(self):
        unstub()

    def test__main__download_files__when_no_existing_local_files(self):
        existing_local_files = []

        when(emoji_bulk_migrator)._get_existing_local_files("path/to/open").thenReturn(existing_local_files)
        when(api_handler).get_emoji_list().thenReturn(existing_remote_files)
        when(emoji_bulk_migrator)._write_local_file(...).thenReturn(None)
        when(api_handler).get_emoji(...).thenReturn(mock_emoji)

        _download_files(api_handler, "path/to/open")
        verify(emoji_bulk_migrator, times=1)._write_local_file("path/to/open", "bowtie.png", mock_emoji)
        verify(emoji_bulk_migrator, times=1)._write_local_file("path/to/open", "squirrel.jpg", mock_emoji)

    def test__main__download_files__with_one_existing_local_file(self):
        existing_local_files = ['squirrel.jpg']
        when(emoji_bulk_migrator)._get_existing_local_files("path/to/open").thenReturn(existing_local_files)
        when(api_handler).get_emoji_list().thenReturn(existing_remote_files)
        when(emoji_bulk_migrator)._write_local_file(...).thenReturn(None)
        when(api_handler).get_emoji(...).thenReturn(mock_emoji)

        _download_files(api_handler, "path/to/open")
        verify(emoji_bulk_migrator, times=1)._write_local_file("path/to/open", "bowtie.png", mock_emoji)
        verify(emoji_bulk_migrator, times=0)._write_local_file("path/to/open", "squirrel.jpg", mock_emoji)

    def test__main__download_files__with_all_files_locally_exist(self):
        existing_local_files = ['squirrel.jpg', 'bowtie.png']
        when(emoji_bulk_migrator)._get_existing_local_files("path/to/open").thenReturn(existing_local_files)
        when(api_handler).get_emoji_list().thenReturn(existing_remote_files)
        when(emoji_bulk_migrator)._write_local_file(...).thenReturn(None)
        when(api_handler).get_emoji(...).thenReturn(mock_emoji)

        _download_files(api_handler, "path/to/open")
        verify(emoji_bulk_migrator, times=0)._write_local_file("path/to/open", "bowtie.png", mock_emoji)
        verify(emoji_bulk_migrator, times=0)._write_local_file("path/to/open", "squirrel.jpg", mock_emoji)

    def test__main__upload_files__when_no_existing_remote_files(self):
        existing_local_files = ['squirrel.jpg', 'bowtie.png', 'octoparty.gif', 'flow.png']
        existing_remote_files = []
        when(emoji_bulk_migrator)._get_existing_local_files("path/to/files").thenReturn(existing_local_files)
        when(emoji_bulk_migrator)._get_existing_remote_files(api_handler).thenReturn(existing_remote_files)
        expect(api_handler).load_emoji(...)

        _upload_files(api_handler, "path/to/files")

        verify(api_handler, times=1).load_emoji(file_name="squirrel.jpg", url="path/to/files/squirrel.jpg")
        verify(api_handler, times=1).load_emoji(file_name="bowtie.png", url="path/to/files/bowtie.png")
        verify(api_handler, times=1).load_emoji(file_name="octoparty.gif", url="path/to/files/octoparty.gif")
        verify(api_handler, times=1).load_emoji(file_name="flow.png", url="path/to/files/flow.png")

    def test__main__upload_files__when_some_existing_remote_files(self):
        existing_local_files = ['squirrel.jpg', 'bowtie.png', 'octoparty.gif', 'flow.png']
        when(emoji_bulk_migrator)._get_existing_local_files("path/to/files").thenReturn(existing_local_files)
        when(api_handler).get_emoji_list().thenReturn(existing_remote_files)
        expect(api_handler).load_emoji(...)

        _upload_files(api_handler, "path/to/files")

        verify(api_handler, times=0).load_emoji(file_name="squirrel.jpg", url="path/to/files/squirrel.jpg")
        verify(api_handler, times=0).load_emoji(file_name="bowtie.png", url="path/to/files/bowtie.png")
        verify(api_handler, times=1).load_emoji(file_name="octoparty.gif", url="path/to/files/octoparty.gif")
        verify(api_handler, times=1).load_emoji(file_name="flow.png", url="path/to/files/flow.png")

    def test__main__upload_files__when_all_existing_remote_files(self):
        existing_local_files = ['squirrel.jpg', 'bowtie.png', 'octoparty.gif', 'flow.png']
        existing_remote_files = {
            "ok": "true",
            "emoji": {
                "bowtie": "https://emoji.slack-edge.com/account_id/bowtie/f3ec6f2bb0.png",
                "squirrel": "https://emoji.slack-edge.com/account_id/squirrel/465f40c0e0.jpg",
                "octoparty": "https://emoji.slack-edge.com/account_id/octoparty/465f40c0e0.gif",
                "flow": "https://emoji.slack-edge.com/account_id/flow/465f40c0e0.png",
                "shipit": "alias:squirrel"
            }
        }
        when(emoji_bulk_migrator)._get_existing_local_files("path/to/files").thenReturn(existing_local_files)
        when(api_handler).get_emoji_list().thenReturn(existing_remote_files)
        expect(api_handler).load_emoji(...)

        _upload_files(api_handler, "path/to/files")

        verify(api_handler, times=0).load_emoji(...)
