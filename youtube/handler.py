import os

import constants
import convertor
import downloader
import validator
from exceptions import DownloadError

AUDIO_FILE_EXTENSION = '.mp3'

def _get_audio_filename(download, file_path):
    """Gets the new filename and extension for the audio version of the video.

    We want to rename the file away from the youtube ID if it's been trimmed, so
    we can prevent a clash in filenames between the trimmed and non-trimmed
    versions.

    Args:
        download: A DownloadRequest object.
        file_path: The file_path to the video file.

    Returns:
        A tuple containing the new file path to the audio file, and the
        extension (hardcoded to be mp3).
    """
    # Remove the file extension from the original file.
    original_file_path = os.path.splitext(file_path)[0]
    trim_suffix = ""
    if download.should_time_trim():
        # Since these are already strings, we can just append them as-is.
        begin, duration = download.get_time_trimming_data()
        trim_suffix = begin + duration

    new_file_path = original_file_path + trim_suffix + AUDIO_FILE_EXTENSION
    return new_file_path, AUDIO_FILE_EXTENSION

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

    try:
        file_path, title = downloader.download(download)
    except:
        raise DownloadError('Error processing file or url')

    file_ext = os.path.splitext(file_path)[1]

    # Convert the video if the selected file type is 'audio'
    if download.is_audio_only():
        new_file_path, file_ext = _get_audio_filename(download, file_path)

        try:
            convertor.convert(file_path, new_file_path, download)
        except Exception as e:
            print 'Conversion Error:', e.message
            raise DownloadError('Error converting video to audio')

    filename = os.path.splitext(os.path.basename(file_path))[0] + file_ext

    output = {
        'filename': filename.encode('ascii', 'xmlcharrefreplace'),
        'title': title + file_ext
    }
    return output
