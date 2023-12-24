import csv
import os
import yt_dlp
from youtubesearchpython import VideosSearch
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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


class Track:
    def __init__(self, title, artist):
        self.title = self.remove_unaccepted_chars(title)
        self.artist = self.remove_unaccepted_chars(artist)

    @staticmethod
    def remove_unaccepted_chars(string):
        return ''.join(c for c in string if c not in UNACCEPTED_CHARS)


def download_track(track):
    search = f"{track.title} {track.artist} lyrics"
    videos_search = VideosSearch(search, limit=1)
    result = videos_search.result()['result']

    if not result:
        print(f"Could not download: {track}")
        return

    url = result[0]['link']

    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        tries = 3
        while tries > 0:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                print("Error while downloading, retrying...")
                tries -= 1
            else:
                break
        else:
            print(f"Skipping this song: {track.title}")
            return

        video_info = ydl.extract_info(url, download=False)
        video_title = video_info['id']
        filename = f"{video_title}"

        os.rename(f"{filename}*", f"{track.title}.mp3")

        artist_dir = Path(f'./Downloaded/{track.artist}')
        artist_dir.mkdir(parents=True, exist_ok=True)

        os.rename(f"{track.title}.mp3", artist_dir / f"{track.title}.mp3")


def main():
    tracks = []

    with open('todownload.csv', encoding="utf-8", newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        tracks = [Track(row[2], row[4].replace(',', '')) for i, row in enumerate(csv_reader) if i > 0]

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_track, tracks)


if __name__ == "__main__":
    main()
