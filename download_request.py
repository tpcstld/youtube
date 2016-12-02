"""Contains data about a download request.
"""
import re
import time

from youtube import constants
from youtube import validator

class DownloadRequest(object):
    TIME_REGEX = re.compile(r"^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$")

    def __init__(self, url, filetype):
        """Constructs a DownloadRequest

        Args:
            url: A string containing the URL of the video, in any format.
            filetype: A string containing the filetype of the output, as either
            'audio' or 'video'
        """
        # Users might not include a protocol, we need to add it.
        if not '//' in url:
            url = '//' + url

        validator.validate_url(download.get_url());
        self.url = url

        # TODO: We should validate that it is either 'audio' or 'video'.
        self.filetype = filetype
        self.force_mp4_filetype = False

        # TODO: Abstract trimming information to its own object.
        self.enable_trim = False
        self.trim_start_secs = None
        self.trim_duration = None

    def get_url(self):
        """Get the Youtube URL to download.

        The URL is guaranteed to be a correct URL, with no extra processing
        required for YoutubeDL to handle it.

        Returns:
            The Youtube URL to download as a string.
        """
        return self.url

    def get_filetype(self):
        """Get the requested filetype of the download.

        Returns:
            Either 'audio' or 'video'
        """
        return self.filetype

    def is_audio_only(self):
        return self.get_filetype() == constants.AUDIO_FILETYPE_NAME

    def set_force_mp4_filetype(self, value):
        self.force_mp4_filetype = value

    def get_force_mp4_filetype(self):
        return self.force_mp4_filetype

    def set_time_trimming(self, start, end):
        """Enables time trimming.

        Args:
            start: A string in the format "HH:MM:SS".
            end: A string in the format "HH:MM:SS".
        """
        def to_seconds(timestr):
            seconds= 0
            for part in timestr.split(':'):
                seconds= seconds*60 + int(part)
            return seconds

        self.enable_trim = True
        self.trim_start = to_seconds(start)
        self.trim_duration = to_seconds(end) - self.trim_start

    def should_time_trim(self):
        """Returns whether or not to trim the video.

        Returns:
            A boolean value indicating whether or not to trim.
        """
        return self.enable_trim

    def get_time_trimming_data(self):
        """Get the start and duration to trim on.

        Returns:
            A tuple (start time, duration).
        """
        return (
            time.strftime('%H:%M:%S', time.gmtime(self.trim_start)),
            time.strftime('%H:%M:%S', time.gmtime(self.trim_duration)))
