import csv
import threading

import yt_dlp
from youtubesearchpython import VideosSearch
import os
from concurrent.futures import ThreadPoolExecutor

YDL_OPTS = {
    'format': 'bestaduio/best',
    'outtmpl': './%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }]
}

UNACCEPTED_CHARS = r'<>:"/\|?*'

failed_tracks = []


def remove_unaccepted_chars(string):
    for char in UNACCEPTED_CHARS:
        string = string.replace(char, '')

    return string


class Track:
    """
    Simple class to store data easily
    """

    def __init__(self, title, artist):
        # removes unaccepted chars for files in Windows
        title = remove_unaccepted_chars(title)
        artist = remove_unaccepted_chars(artist)

        self.title = title
        self.artist = artist


def download_track(track):
    search = f"{track.title} {track.artist} lyrics"
    videos_search = VideosSearch(search, limit=1)
    result = videos_search.result()['result']

    if not result:
        print(f"Could not download: {track}")

    url = result[0]['link']

    # download song
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:

        downloaded = False
        tries = 3
        while not downloaded:
            try:
                z = ydl.download([url])
                downloaded = True
            except yt_dlp.utils.DownloadError:
                downloaded = False
                tries -= 1

                print("Error while downloading, retrying...")

                if tries < 1:
                    downloaded = True
                    print(f"Skipping this song: {track.title}")
                    failed_tracks.append(track)

    video_info = ydl.extract_info(url, download=False)
    video_title = video_info['id']
    filename = f"{video_title}"

    print(f'move "{filename}*" "{track.title}.mp3"')
    os.system(f'move "{filename}*" "{track.title}.mp3"')

    if not os.path.isdir(f'./Downloaded/{track.artist}'):
        os.system(f'mkdir "Downloaded/{track.artist}"')

    # move song to it's arist's directory
    os.system(f'move "{track.title}.mp3" "Downloaded/{track.artist}/{track.title}.mp3"')


tracks = []

# create folder if it doesn't exist
if not os.path.isdir('./Downloaded/'):
    os.system('mkdir Downloaded')

with open('todownload.csv', encoding="utf-8", newline='') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for i, row in enumerate(csv_reader):
        # first line stores information about column names, have to skip it
        if i > 0:
            track = Track(row[2], row[4].replace(',', ''))
            tracks.append(track)

with ThreadPoolExecutor(max_workers=5) as executor:
    for track in tracks:
        executor.submit(download_track, track)

print("Failed to download: ")
if tracks:
    for track in tracks:
        print(f"{track.title} {track.artist}")
else:
    print("None")
