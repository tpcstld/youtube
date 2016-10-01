import os

import constants
import convertor
import downloader
import validator
from exceptions import DownloadError

# TODO: Return a namedtuple instead.
def initate_download(download):
    """Validates, downloads and possibly converts the video, depending on filetype

    Args:
        download: A DownloadRequest object.

    Returns:
        A dict containing the filename and title of the video. The filename is
        the name of the file stored inside the 'temp' folder. The title is the
        original title of the video.

    Raises:
        DownloadError: if something went wrong during the download
    """
    # Log the download
    print 'Downloading', download.get_url(), 'in', download.get_filetype(), 'format'

    # Ensure that the url is correct
    # TODO: Remove
    validator.validate_url(download.get_url())
    try:
        file_path, title = downloader.download(download)
    except:
        raise DownloadError('Error processing file or url')

    file_ext = os.path.splitext(file_path)[1]

    # Convert the video if the selected file type is 'audio'
    # TODO: Implement is_audio in DownloadRequest.
    if download.is_audio_only():
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
