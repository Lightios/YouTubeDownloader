import csv
import yt_dlp
from youtubesearchpython import VideosSearch
import os

YDL_OPTS = {
    'format': 'bestaduio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }]
}

UNACCEPTED_CHARS = '<>:"/\\|?*'


class Track:
    """
    Simple class for storing data easily
    """

    def __init__(self, title, artist):
        # removes unaccepted chars for files in Windows
        for char in UNACCEPTED_CHARS:
            title = title.replace(char, '')
            artist = artist.replace(char, '')

        self.title = title
        self.artist = artist


tracks = []

# creates folder if it doesn't exist
if not os.path.isdir('./Downloaded/'):
    os.system('mkdir Downloaded')

with open('todownload.csv', encoding="utf-8", newline='') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for i, row in enumerate(csv_reader):
        # first line stores information about column names, it has to skip it
        if i > 0:
            track = Track(row[2], row[4].replace(',', ''))
            tracks.append(track)
        # else:
            # print(f'Column names are {", ".join(row)}')

for track in tracks:
    search = f"{track.title} {track.artist}"
    videosSearch = VideosSearch(search, limit=1)
    url = videosSearch.result()['result'][0]['link']

    # downloads song
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        ydl.download([url])

    # looks for downloaded file in current directory
    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            # renames song from weird name to track's title
            os.system(f'move "{file}" "{track.title}.mp3"')

            # create a new folder for current artist if it doesn't exist
            if not os.path.isdir(f'./Downloaded/{track.artist}'):
                os.system(f'mkdir "Downloaded/{track.artist}"')

            # moves song to it's arist's directory
            os.system(f'move "{track.title}.mp3" "Downloaded/{track.artist}/{track.title}.mp3"')
