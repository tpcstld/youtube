import os

from youtube_dl import YoutubeDL
from youtube_dl import MaxDownloadsReached

def download(url):
    """Downloads the youtube video from the url

    Args:
        url: The youtube URL pointing to the video to download.

    Returns:
        A (file name, video title) tuple.

    The file name is ONLY the file name, and does not include the file path.
    """
    downloader = YoutubeDL()
    downloader.add_default_info_extractors()

    downloader.params['outtmpl'] = os.path.join(os.getcwd(),
                                                'temp/%(id)s.%(ext)s')
    downloader.params['verbose'] = True
    downloader.params['cachedir'] = None
    downloader.params['noplaylist'] = True
    downloader.params['max_downloads'] = 1

    try:
        info = downloader.extract_info(url)
    except MaxDownloadsReached:
        info = downloader.extract_info(url, download=False)

    file_name = downloader.prepare_filename(info)
    file_name = file_name.encode('ascii', 'ignore')

    title = info.get('title', os.path.basename(file_name))
    return file_name, title
