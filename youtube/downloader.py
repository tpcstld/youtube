import os

from youtube_dl import YoutubeDL
from youtube_dl import MaxDownloadsReached

# TODO: Add progress bar feature.
def download(download):
    """Downloads the youtube video from the url

    Args:
        download: A DownloadRequest.

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

    if download.is_audio_only():
        downloader.params['format'] = 'bestaudio'
    else:
        # We are only going to support downloading .mp4 videos.
        downloader.params['format'] = 'mp4'

    if download.get_force_mp4_filetype():
        downloader.params['format'] = 'mp4'

    info = downloader.extract_info(download.get_url())

    file_name = downloader.prepare_filename(info)
    file_name = file_name.encode('ascii', 'ignore')

    title = info.get('title', os.path.basename(file_name))
    return file_name, title
