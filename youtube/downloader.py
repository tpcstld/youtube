import os

from youtube_dl import YoutubeDL
from youtube_dl import MaxDownloadsReached

def download(url):
    """Downloads the youtube video from the url

    Returns:
        A tuple containing the filename (not filepath) to the downloaded file
        and the title of the video
    """
    downloader = YoutubeDL()
    downloader.add_default_info_extractors()

    # Prepend 'finished_' to get rid of annoying conversion error
    downloader.params['outtmpl'] = os.path.join(os.getcwd(), 'temp/finished_%(id)s.%(ext)s')
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
