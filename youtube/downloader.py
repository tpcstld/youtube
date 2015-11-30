import os

from youtube_dl import YoutubeDL
from youtube_dl import MaxDownloadsReached

def download(url, audio_only):
    """Downloads the youtube video from the url

    Args:
        url: The youtube URL pointing to the video to download.
        audio_only: True if we only want to download the best audio.

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
    downloader.params['format'] = 'mp4'

    try:
        info = downloader.extract_info(url)
    except MaxDownloadsReached:
        info = downloader.extract_info(url, download=False)
    except Exception:
        # We don't really have to do this, but YoutubeDL sometimes has a problem
        # combining the video and audio portions of webm files, so this is a
        # good workaround since we really only care about the audio part.
        if audio_only:
            downloader.params['format'] = 'bestaudio'
        else:
          raise

        try:
            info = downloader.extract_info(url)
        except MaxDownloadsReached:
            info = downloader.extract_info(url, download=False)

    file_name = downloader.prepare_filename(info)
    file_name = file_name.encode('ascii', 'ignore')

    title = info.get('title', os.path.basename(file_name))
    return file_name, title
