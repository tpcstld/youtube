import os

import constants
import convertor
import downloader
import validator
from exceptions import DownloadError

def initate_download(url, filetype):
    """Validates, downloads and possibly converts the video, depending on filetype

    Args:
        url(str): The URL for the video to download
        filetype(str): The desired filetype (video or audio)

    Returns:
        A dict containing the filename and title of the video. The filename is
        the name of the file stored inside the 'temp' folder. The title is the
        original title of the video.

    Raises:
        DownloadError: if something went wrong during the download
    """
    # Log the download
    print 'Downloading', url, 'in', filetype, 'format'

    # Ensure that the url is correct
    validator.validate_url(url)
    try:
        file_path, title = downloader.download(
            url, filetype == constants.AUDIO_FILETYPE_NAME)
    except:
        raise DownloadError('Error processing file or url')

    file_ext = os.path.splitext(file_path)[1]

    # Convert the video if the selected file type is 'audio'
    if filetype == constants.AUDIO_FILETYPE_NAME:
        original_file_path = os.path.splitext(file_path)[0]  # No file extension
        file_ext = '.mp3'
        new_file_path = original_file_path + file_ext
        try:
            convertor.convert(file_path, new_file_path)
        except Exception as e:
            print 'Conversion Error:', e.message
            raise DownloadError('Error converting video to audio')

    filename = os.path.splitext(os.path.basename(file_path))[0] + file_ext

    output = {
        'filename': filename.encode('ascii', 'xmlcharrefreplace'),
        'title': title + file_ext
    }
    return output
