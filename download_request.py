"""Contains data about a download request.
"""
import re

from youtube import constants
from youtube.exceptions import ValidationError

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

        self.url = url
        self.filetype = filetype
        self.force_mp4_filetype = False

        # TODO: Move to it's own object.
        self.enable_trim = False

        # These are strings to be passed into ffmpeg.
        self.trim_start = None
        self.trim_end = None

    def get_url(self):
        return self.url

    def get_filetype(self):
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
            start: A string in the format "HH:MM:SS" to be passed into ffmpeg.
            end: A string in the format "HH:MM:SS" to be passed into ffmpeg.
        """
        if not self.TIME_REGEX.match(start) or not self.TIME_REGEX.match(end):
            raise ValidationError("Bad time format.")

        self.enable_trim = True
        self.trim_start = start
        self.trim_end = end

    def should_time_trim(self):
        """Returns whether or not to trim the video.

        Returns:
            A boolean value indicating whether or not to trim.
        """
        return self.enable_trim

    def get_time_trimming_data(self):
        """Get the start and end time to trim on.

        Returns:
            A tuple (start time, end time).
        """
        return (self.trim_start, self.trim_end)
