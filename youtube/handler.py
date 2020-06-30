import os

from . import constants
from . import convertor
from . import downloader
from . import validator
from .exceptions import DownloadError

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
        A string containing the new file path to the audio file.
    """
    # Remove the file extension from the original file.
    original_file_path = os.path.splitext(file_path)[0]
    trim_suffix = ""
    if download.should_time_trim():
        # Since these are already strings, we can just append them as-is.
        begin, duration = download.get_time_trimming_data()
        trim_suffix = begin + duration

    new_file_path = str(original_file_path) + trim_suffix + AUDIO_FILE_EXTENSION
    return new_file_path

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
    print('Downloading', download.get_url(), 'in', download.get_filetype(), 'format')

    try:
        file_path, title = downloader.download(download)
    except:
        raise DownloadError('Error processing file or url')

    final_filepath = file_path

    # Convert the video if the selected file type is 'audio'
    if download.is_audio_only():
        final_filepath = _get_audio_filename(download, file_path)

        try:
            convertor.convert(str(file_path), str(final_filepath), download)
        except Exception as e:
            print('Conversion Error:', e.message)
            raise DownloadError('Error converting video to audio')

    filename = os.path.basename(final_filepath)
    file_ext = os.path.splitext(filename)[1]

    output = {
        'filename': filename.encode('ascii', 'xmlcharrefreplace').decode('utf-8'),
        'title': title + file_ext
    }
    return output
