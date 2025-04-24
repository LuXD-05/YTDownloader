# Python Youtube Downloader

This is an application which provides a GUI to search and download videos from Youtube with some basic options. Currently it does NOT support playlist download.

## Usage

Before starting to search for videos you need to specify your YouTube API key in the settings in the top-right corner.

You can create your own API key by following these steps: https://developers.google.com/youtube/v3/getting-started#before-you-start

## Problems

Currently, the playlist download is not supported. The wanted behavior is that, with the split-chapters flag checked, the app uses YT-DLP to download each video, eventually splitting those that have chapters.

I still haven't figured out how to conditionally format the YT-DLP template string so that, if the playlist's video has no chapters, it is created in the folder "[default_download_path]\[playlist_title]" normally, otherwise all its chapters end up in "[default_download_path]\[playlist_title]\[video_title]".

This is in "downloader.py" in the "download_item" function.

## Todo

0) PACKAGE TO ANDROID (also after some?)
1) Handle history (new py file) & add its view
2) Btn "Delete selected" to delete all selected videos
3) Download function (playlist download)

### Eventual todos
1) SPOTIFY DOWNLOAD LOGICx
2) Confirm 1-by-1 setting (while downloading, handles video's options 1-by-1)
3) Btn/popup for file import (+ define import file structure)